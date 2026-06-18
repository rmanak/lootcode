"""Sandbox harness — runs INSIDE the isolated subprocess/container.

Trusted code (part of the sandbox boundary). Must not import anything from the
`app` package: it runs with a minimal environment and only the standard library.

Reads  <workdir>/payload.json  and  <workdir>/solution.py
Writes <workdir>/result.json   = {"results": [{name, status, returned?, time_ms,
                                  error?, stdout}]}

Per-test wall-clock limits are enforced with SIGALRM; the parent process applies
CPU/memory/PID/file-size rlimits and an overall kill-timeout as a backstop.
"""
from __future__ import annotations

import importlib.util
import io
import json
import os
import signal
import sys
import time
import traceback


class _Timeout(Exception):
    pass


def _on_alarm(signum, frame):  # noqa: ANN001
    raise _Timeout()


def _short_tb(limit: int = 2000) -> str:
    tb = traceback.format_exc()
    return tb[-limit:]


def _load_solution(path: str, budget_s: float):
    """Import the user's solution.py, guarding against import-time hangs."""
    signal.setitimer(signal.ITIMER_REAL, budget_s)
    try:
        spec = importlib.util.spec_from_file_location("solution", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        return module, None
    except _Timeout:
        return None, "Import timed out (module-level code took too long)."
    except BaseException:  # noqa: BLE001 - report anything, incl. SystemExit
        return None, "Error while loading your solution:\n" + _short_tb()
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)


def _run_one(func, params, inp, time_limit_s, max_output) -> dict:
    buf = io.StringIO()
    real_stdout = sys.stdout
    start = time.perf_counter()
    try:
        args = {p: inp[p] for p in params}
    except KeyError as exc:
        return {"status": "error", "error": f"Missing input for parameter {exc}.",
                "time_ms": 0, "stdout": ""}
    try:
        sys.stdout = buf
        signal.setitimer(signal.ITIMER_REAL, time_limit_s)
        returned = func(**args)
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout
        elapsed = (time.perf_counter() - start) * 1000
        try:
            json.dumps(returned)
        except (TypeError, ValueError):
            return {"status": "error", "time_ms": elapsed,
                    "error": f"Return value is not JSON-serializable: {type(returned).__name__}",
                    "stdout": buf.getvalue()[:max_output]}
        return {"status": "ok", "returned": returned, "time_ms": elapsed,
                "stdout": buf.getvalue()[:max_output]}
    except _Timeout:
        return {"status": "timeout", "time_ms": time_limit_s * 1000,
                "error": "Time limit exceeded.", "stdout": buf.getvalue()[:max_output]}
    except BaseException:  # noqa: BLE001
        elapsed = (time.perf_counter() - start) * 1000
        return {"status": "error", "time_ms": elapsed, "error": _short_tb(),
                "stdout": buf.getvalue()[:max_output]}
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        sys.stdout = real_stdout


def main() -> None:
    workdir = sys.argv[1]
    with open(os.path.join(workdir, "payload.json"), encoding="utf-8") as f:
        payload = json.load(f)

    fn_name = payload["function_name"]
    params = payload["params"]
    tests = payload["tests"]
    max_output = int(payload.get("max_output_bytes", 65536))

    signal.signal(signal.SIGALRM, _on_alarm)

    module, load_err = _load_solution(
        os.path.join(workdir, "solution.py"), float(payload.get("import_budget_s", 5.0))
    )
    func = getattr(module, fn_name, None) if module else None
    if module and func is None:
        load_err = f"Your solution must define a function named `{fn_name}`."

    results = []
    for t in tests:
        if load_err or func is None:
            results.append({"name": t["name"], "status": "error",
                            "error": load_err or "Function not found.",
                            "time_ms": 0, "stdout": ""})
            continue
        out = _run_one(func, params, t["input"], float(t["time_limit_s"]), max_output)
        out["name"] = t["name"]
        results.append(out)

    with open(os.path.join(workdir, "result.json"), "w", encoding="utf-8") as f:
        json.dump({"results": results}, f)


if __name__ == "__main__":
    main()
