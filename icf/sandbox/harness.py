"""ICF sandbox harness — runs INSIDE the isolated subprocess/container.

Trusted code (part of the sandbox boundary), and the ICF counterpart of
``app/executor/harness.py``. Stdlib only: it may not import anything from
``app`` or from the rest of ``icf``.

Reads  <workdir>/payload.json
       <workdir>/solution.py            the solver's code (untrusted)
       <workdir>/icf_testkit.py         the assertion kit
       <workdir>/<test modules>.py      authored cases (trusted repo content)
Writes <workdir>/result.json = {"load_error": str|null,
                                "results": [{id, status, message, time_ms, stdout}]}

``status`` is one of: passed | failed | timeout | error.  *failed* is an
expectation that did not hold (the solver's bug); *error* is an exception the
case did not expect, or a problem loading the solution.

## Two processes, on purpose

The core executor keeps the judge out of the sandbox entirely: expected values
never go in, and the parent compares what came back
(`docs/code-execution.md`). ICF cannot do that — its oracle *is* code, and it
has to run beside the solution — so the separation moves one level down:

* the **supervisor** (this process) imports the trusted test modules, deletes
  their source files from the run directory, forks the worker, and is the only
  process that ever writes ``result.json``;
* the **worker** (its child) imports ``solution.py`` and runs the cases,
  reporting each one over a pipe as it finishes.

So untrusted code cannot write the results file, cannot read the test sources
off disk, and cannot make the supervisor report a case it never ran: a worker
that dies, hangs or goes silent leaves the remaining cases marked failed by
the supervisor, never passed. What it *can* still do is lie about a verdict
inside its own process (by patching the testkit, say) — see
``icf/docs/security.md``; hidden cases are run in a separate sandbox whose
output is discarded, so that buys a cheat, never a leak.

Per-case wall-clock limits are enforced with SIGALRM in the worker, with the
supervisor holding a backstop timer; the parent process applies
CPU/memory/PID/file-size rlimits and an overall kill-timeout on top.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import shutil
import signal
import sys
import time
import traceback

#: A message from the solver's code (an assertion, a traceback) is unbounded
#: and untrusted. Clip it where it is produced: an unclipped one megabyte of
#: it hits the file-size rlimit while result.json is being written and costs
#: every case its result.
MAX_MESSAGE_CHARS = 2000

#: Backstop the supervisor allows a case on top of the worker's own SIGALRM.
WORKER_GRACE_S = 2.0

#: Ceiling on one message from the worker. Everything in a case result is
#: already clipped before it is sent, so a longer line means the worker is
#: writing to the pipe on its own account — and an unbounded `readline` would
#: buffer it all in the supervisor before noticing.
MAX_MESSAGE_BYTES = 1 << 20


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):  # noqa: ANN001
    raise _Timeout()


_TRUNCATED = "\n... [output truncated — your solution printed too much]"


class _OutputBudget:
    """A cap on captured stdout for the WHOLE run, not per case.

    Same reasoning as the core harness: result.json holds every case's output
    and the parent sizes RLIMIT_FSIZE for one file, so a per-case cap would
    multiply by the number of cases and a print-in-a-loop solution would kill
    the process mid-write, losing every result.
    """

    def __init__(self, total: int) -> None:
        self.total = max(total, 0)
        self.remaining = self.total

    def new_buffer(self):
        return _CappedBuffer(self.total)

    def take(self, text: str) -> str:
        if len(text) <= self.remaining:
            self.remaining -= len(text)
            return text
        kept = text[:self.remaining]
        self.remaining = 0
        return kept + _TRUNCATED


class _CappedBuffer:
    """A `sys.stdout` stand-in that stops storing past `limit` characters.

    Not an io.StringIO: that grows without bound (OOM on a print bomb) and
    raises from `getvalue()` after a solver calls `sys.stdout.close()`. Here
    close/flush are no-ops and reads never raise.
    """

    def __init__(self, limit: int) -> None:
        self._parts: list[str] = []
        self._len = 0
        self._limit = max(limit, 0)
        self._dropped = False
        self.closed = False

    def write(self, s) -> int:
        text = s if isinstance(s, str) else str(s)
        room = self._limit - self._len
        if len(text) > room:
            self._dropped = True
        if room > 0:
            self._parts.append(text[:room])
            self._len += min(len(text), room)
        return len(text)

    def writelines(self, lines) -> None:
        for line in lines:
            self.write(line)

    def getvalue(self) -> str:
        return "".join(self._parts) + (_TRUNCATED if self._dropped else "")

    def flush(self) -> None:
        pass

    def close(self) -> None:
        pass

    def isatty(self) -> bool:
        return False

    def writable(self) -> bool:
        return True

    def readable(self) -> bool:
        return False


def _value(buf) -> str:
    try:
        return buf.getvalue()
    except Exception:  # noqa: BLE001 - never let output capture fail a run
        return ""


def _clip(text: str | None) -> str | None:
    if text is None:
        return None
    if len(text) <= MAX_MESSAGE_CHARS:
        return text
    return text[:MAX_MESSAGE_CHARS] + "… [message truncated]"


def _short_tb() -> str:
    """The user-facing text for an unexpected exception."""
    text = traceback.format_exc()
    if len(text) > MAX_MESSAGE_CHARS:
        text = "…\n" + text[-MAX_MESSAGE_CHARS:]
    return text.strip()


def _import_module(path: str, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


# --- the worker: everything below runs with the solver's code loaded --------

def _load_solution(workdir: str, budget_s: float, out_budget):
    """Import the solver's module, capturing its output and bounding its time."""
    buf = out_budget.new_buffer()
    real_stdout = sys.stdout
    try:
        sys.stdout = buf
        signal.setitimer(signal.ITIMER_REAL, budget_s)
        module = _import_module(os.path.join(workdir, "solution.py"), "solution")
        signal.setitimer(signal.ITIMER_REAL, 0)
        return module, None, out_budget.take(_value(buf))
    except _Timeout:
        return None, ("Your code took too long to import — is there work "
                      "running at module level?"), out_budget.take(_value(buf))
    except BaseException:  # noqa: BLE001 - any import failure is the solver's
        return None, _short_tb(), out_budget.take(_value(buf))
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _run_case(fn, cls, time_limit_s: float, out_budget) -> dict:
    """Run one case against the solver's class under its own time limit."""
    buf = out_budget.new_buffer()
    real_stdout = sys.stdout
    start = time.perf_counter()
    try:
        sys.stdout = buf
        signal.setitimer(signal.ITIMER_REAL, time_limit_s)
        fn(cls)
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout
        return {"status": "passed", "message": None,
                "time_ms": (time.perf_counter() - start) * 1000,
                "stdout": out_budget.take(_value(buf))}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "message": "Time limit exceeded.",
                "stdout": out_budget.take(_value(buf))}
    except AssertionError as exc:
        # Both `expect(...)` and a bare `assert` land here: the solver's answer
        # was wrong, which is a failure, not a crash.
        return {"status": "failed", "message": _clip(str(exc)) or "Assertion failed.",
                "time_ms": (time.perf_counter() - start) * 1000,
                "stdout": out_budget.take(_value(buf))}
    except BaseException:  # noqa: BLE001 - anything else is an unexpected error
        return {"status": "error", "message": _short_tb(),
                "time_ms": (time.perf_counter() - start) * 1000,
                "stdout": out_budget.take(_value(buf))}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def _emit(stream, message: dict) -> None:
    """One newline-delimited JSON message from the worker to the supervisor."""
    stream.write(json.dumps(message) + "\n")
    stream.flush()


def _worker(workdir: str, payload: dict, registry: dict, write_fd: int) -> None:
    """Child process: import the solution, run every case, report each one.

    Never returns — it always ends in ``os._exit`` so no exception can unwind
    past the fork and leave two supervisors running.
    """
    stream = os.fdopen(write_fd, "w", encoding="utf-8")
    try:
        out_budget = _OutputBudget(int(payload.get("max_output_bytes", 65536)))
        signal.signal(signal.SIGALRM, _on_alarm)

        module, load_err, import_out = _load_solution(
            workdir, float(payload.get("import_budget_s", 5.0)), out_budget)

        class_name = payload.get("class_name") or ""
        cls = getattr(module, class_name, None) if module else None
        if module is not None and cls is None:
            load_err = f"Your solution must define a class named `{class_name}`."
        elif cls is not None and not isinstance(cls, type):
            load_err = f"`{class_name}` is defined in your solution but is not a class."
            cls = None

        _emit(stream, {"type": "load", "error": _clip(load_err),
                       "stdout": import_out})
        if load_err or cls is None:
            os._exit(0)

        first = True
        for spec in payload.get("cases", []):
            entry = registry.get((spec["module"], spec["func"]))
            if entry is None:
                _emit(stream, {"type": "case", "id": spec["id"], "status": "error",
                               "time_ms": 0, "stdout": "",
                               "message": (f"Test case `{spec['func']}` is missing "
                                           f"from `{spec['module']}` — the problem "
                                           "is misconfigured.")})
                continue
            _label, fn = entry
            out = _run_case(fn, cls, float(spec.get("time_limit_s", 5.0)), out_budget)
            if first:
                # Output printed while the solution was being imported belongs
                # to the run, not to any one case: show it on the first one.
                out["stdout"] = import_out + out["stdout"]
                first = False
            out["type"] = "case"
            out["id"] = spec["id"]
            _emit(stream, out)
    except BaseException:  # noqa: BLE001, S110 - the supervisor fills in the rest
        # Whatever went wrong here, the cases the supervisor never heard about
        # are marked failed by it. Reporting the crash from inside the process
        # that crashed is not something to rely on.
        pass
    finally:
        with contextlib.suppress(Exception):
            stream.close()
        os._exit(0)


# --- the supervisor: never imports the solution -----------------------------

def _collect_cases(workdir: str, module_names: list[str], testkit) -> dict:
    """Import each authored test module and index its cases by (module, func).

    Test modules are repo content, not user input: an exception here is a bug
    in the problem, and it is reported as such rather than blamed on the
    solver.
    """
    found: dict[tuple[str, str], tuple[str, object]] = {}
    for name in module_names:
        testkit.drain()  # anything left over from a previous module
        _import_module(os.path.join(workdir, name + ".py"), name)
        for func_name, label, fn in testkit.drain():
            found[(name, func_name)] = (label, fn)
    return found


def _hide_test_sources(workdir: str, module_names: list[str]) -> None:
    """Delete the test modules from disk once they are imported.

    They are the oracle. The worker is forked *after* this, so the solver's
    code never shares a filesystem with the cases that grade it — reading
    `icf_tests_l3_hidden.py` and printing it was otherwise a three-line
    submission.

    The compiled copies have to go with them. `python -I` implies `-E`, so the
    `PYTHONDONTWRITEBYTECODE=1` the parent sets in the environment is ignored
    and importing a test module leaves `__pycache__/<name>.cpython-*.pyc` in
    the run directory — which holds every string constant in the file, i.e.
    every expected value. `sys.dont_write_bytecode` is set in `main` as well,
    so ordinarily there is nothing here to delete.
    """
    doomed = [f"{name}.py" for name in module_names]
    # payload.json goes too: it lists every case id, hidden ones included.
    doomed.append("payload.json")
    for filename in doomed:
        with contextlib.suppress(OSError):
            os.unlink(os.path.join(workdir, filename))
    shutil.rmtree(os.path.join(workdir, "__pycache__"), ignore_errors=True)


def _open_result(path: str):
    """Open result.json for writing, never through whatever the solution left there.

    The run directory belongs to untrusted code by the time this runs. A
    submission that plants a fifo at `result.json` makes a plain `open(...,
    "w")` block until the parent's overall timeout — a whole run's budget,
    burned from one line of user code — and a symlink would have us write
    wherever it points. So: remove what is there, then create it ourselves and
    refuse to follow a link.
    """
    with contextlib.suppress(OSError):
        os.unlink(path)
    flags = (os.O_WRONLY | os.O_CREAT | os.O_EXCL
             | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    # 0644, not 0600: on the docker backend this file is created by the
    # container's `nobody` and read back by the server's user. The run
    # directory it sits in is private (sandbox.make_workdir), so the mode of
    # the file inside it is not what keeps a submission private.
    return os.fdopen(os.open(path, flags, 0o644), "w", encoding="utf-8")


def _write(workdir: str, payload: dict) -> None:
    """Write result.json, degrading rather than dying if it does not fit.

    The same ladder as the core harness: a run that produced results and then
    could not write them reports nothing at all, which is the worst outcome
    available.
    """
    path = os.path.join(workdir, "result.json")
    attempts = [payload]

    stripped = {**payload, "results": [{**r, "stdout": ""} for r in payload["results"]]}
    attempts.append(stripped)

    minimal = {"load_error": payload.get("load_error"),
               "results": [{"id": r.get("id"), "status": r.get("status", "error"),
                            "message": None, "time_ms": 0, "stdout": ""}
                           for r in payload["results"]]}
    attempts.append(minimal)

    for candidate in attempts:
        try:
            with _open_result(path) as fh:
                json.dump(candidate, fh)
            return
        except OSError:
            continue


def _read_worker(read_fd: int, cases: list, import_budget_s: float) -> tuple:
    """Consume the worker's stream, holding a backstop timer over every read.

    Returns ``(load_error, results_by_id)``. Anything the worker did not
    report — because it hung, crashed, or exited early — is simply absent, and
    the caller marks it failed. This is the fail-closed half of the split: a
    verdict has to arrive to count.
    """
    by_id: dict[str, dict] = {}
    load_error = None
    timed_out = False
    buffer = bytearray()
    exhausted = False

    def read_line(budget_s: float) -> bytes | None:
        """One newline-terminated message, or None. Bounded: a worker that
        writes a gigabyte without a newline costs us a megabyte, not a run."""
        nonlocal exhausted
        signal.setitimer(signal.ITIMER_REAL, budget_s)
        try:
            while True:
                end = buffer.find(b"\n")
                if end != -1:
                    line = bytes(buffer[:end])
                    del buffer[:end + 1]
                    return line
                if exhausted or len(buffer) > MAX_MESSAGE_BYTES:
                    return None
                chunk = os.read(read_fd, 65536)
                if not chunk:
                    exhausted = True
                    return None
                buffer.extend(chunk)
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)

    def read_one(budget_s: float):
        line = read_line(budget_s)
        if not line:
            return None
        try:
            message = json.loads(line.decode("utf-8", "replace"))
        except ValueError:
            return None
        return message if isinstance(message, dict) else None

    try:
        header = read_one(import_budget_s + WORKER_GRACE_S)
        if header is None:
            return None, by_id, True
        load_error = header.get("error")
        if load_error:
            return _as_text(load_error), by_id, False

        for spec in cases:
            message = read_one(float(spec.get("time_limit_s", 5.0)) + WORKER_GRACE_S)
            if message is None:
                break
            case_id = message.get("id")
            if isinstance(case_id, str):
                by_id[case_id] = message
    except _Timeout:
        timed_out = True
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        with contextlib.suppress(OSError):
            os.close(read_fd)
    return (_as_text(load_error) if load_error else None), by_id, timed_out


def _as_text(value) -> str:
    return value if isinstance(value, str) else str(value)


def _reap(pid: int) -> None:
    """Kill the worker (it may still be spinning) and clear the zombie."""
    with contextlib.suppress(ProcessLookupError, PermissionError):
        os.kill(pid, signal.SIGKILL)
    with contextlib.suppress(ChildProcessError):
        os.waitpid(pid, 0)


def main() -> None:
    # `python -I` ignores PYTHONDONTWRITEBYTECODE, and a .pyc of a test module
    # is a readable copy of the oracle. Ask for it in-process instead.
    sys.dont_write_bytecode = True
    workdir = os.path.abspath(sys.argv[1])
    # sys.path[0] is the directory this harness was launched from, which is
    # part of the application. Replace it with the run directory: the solver's
    # code then sees only its own files plus the stdlib, and `import
    # icf_testkit` from a test module resolves to the copy in the workdir.
    sys.path[0] = workdir

    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as fh:
        payload = json.load(fh)

    cases = payload.get("cases", [])
    signal.signal(signal.SIGALRM, _on_alarm)

    testkit = _import_module(os.path.join(workdir, "icf_testkit.py"), "icf_testkit")
    module_names = payload.get("modules", [])
    try:
        registry = _collect_cases(workdir, module_names, testkit)
    except BaseException:  # noqa: BLE001 - a broken test module, not a broken solution
        broken = "This problem's test module failed to load:\n" + _short_tb()
        _write(workdir, {
            "load_error": broken,
            "results": [{"id": c["id"], "status": "error", "message": broken,
                         "time_ms": 0, "stdout": ""} for c in cases]})
        return

    _hide_test_sources(workdir, module_names)

    read_fd, write_fd = os.pipe()
    try:
        pid = os.fork()
    except OSError as exc:
        # No process slots left (RLIMIT_NPROC counts every task the machine's
        # user already owns, not just ours). Say so: the alternative is dying
        # here and reporting "the process was killed" for every case.
        os.close(read_fd)
        os.close(write_fd)
        broken = (f"The grader could not start a worker process ({exc}). This "
                  "is a problem with the server, not with your solution.")
        _write(workdir, {"load_error": broken,
                         "results": [{"id": c["id"], "status": "error",
                                      "message": broken, "time_ms": 0,
                                      "stdout": ""} for c in cases]})
        return
    if pid == 0:
        os.close(read_fd)
        _worker(workdir, payload, registry, write_fd)  # never returns
        return  # pragma: no cover
    os.close(write_fd)

    load_error, by_id, timed_out = _read_worker(
        read_fd, cases, float(payload.get("import_budget_s", 5.0)))
    _reap(pid)

    missing_message = (
        "Your solution's run ended before this case reported a result "
        "(time limit, a crash, or the process exited)."
    )
    results = []
    for spec in cases:
        reported = by_id.get(spec["id"])
        if reported is None:
            results.append({
                "id": spec["id"],
                "status": "timeout" if timed_out else "error",
                "message": load_error or missing_message,
                "time_ms": 0, "stdout": ""})
            continue
        results.append({
            "id": spec["id"],
            # A verdict the worker invents is still only a verdict about its
            # own case; the supervisor decides the shape and the vocabulary.
            "status": (reported.get("status")
                       if reported.get("status") in
                       ("passed", "failed", "timeout", "error") else "error"),
            "message": _clip(_as_text(reported.get("message"))
                             if reported.get("message") is not None else None),
            "time_ms": (reported.get("time_ms")
                        if isinstance(reported.get("time_ms"), int | float) else 0),
            "stdout": (reported.get("stdout")
                       if isinstance(reported.get("stdout"), str) else ""),
        })

    _write(workdir, {"load_error": load_error, "results": results})


if __name__ == "__main__":
    main()
