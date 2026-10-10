"""The sandbox launcher: run a trusted harness over untrusted files.

This is the process-level half of the executor — everything that is true no
matter *what* the harness grades. It was the body of ``subprocess_executor.run``
until a second kind of grader needed the same boundary; rather than keep two
copies of a security control in the tree, the launch lives here once and the
callers supply their own harness and payload.

Guarantees (see docs/code-execution.md), unchanged by the extraction: per-run
CPU/wall-time limits, an address-space (memory) cap, a process cap (anti
fork-bomb), a file-size cap, a minimal environment with no secrets, its own
process group (killed as a group on timeout), and a throwaway working directory
deleted afterwards.

NOTE: a subprocess does NOT block network access. For untrusted multi-user
deployments use the `docker` backend.

The contract with a harness is a directory:

    <workdir>/payload.json   what to run (written here)
    <workdir>/<files…>       solution + whatever else the caller supplies
    <workdir>/result.json    what the harness writes back

and the command ``python -I <harness> <workdir>``.
"""
from __future__ import annotations

import contextlib
import json
import os
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import uuid
from collections.abc import Mapping

from ..config import settings
from ..logging_config import get_logger
from .base import Limits

log = get_logger(__name__)

# Room in the file-size rlimit for the JSON around the captured output: every
# test's returned value, name, status and timing. Still small enough that the
# cap remains a real anti-disk-fill control (the workdir is deleted afterwards).
RESULT_HEADROOM_BYTES = 1024 * 1024

#: Ceiling on the result file we are willing to read back. The harness's own
#: budget is `max_output_kb + RESULT_HEADROOM_BYTES`, enforced by RLIMIT_FSIZE,
#: so anything past twice the headroom is not a result — it is an attack.
MAX_RESULT_BYTES = 2 * RESULT_HEADROOM_BYTES

#: How many extra tasks a sandboxed run may create beyond what the machine is
#: already running. This is the anti-fork-bomb budget.
TASK_SLACK = 64
#: Floor for that budget, so a machine we cannot measure still gets a cap.
MIN_TASK_LIMIT = 256

try:
    import resource  # POSIX only
except ImportError:  # pragma: no cover - Windows fallback
    resource = None  # type: ignore[assignment]  # every use is guarded by `is None`


def _user_task_count() -> int:
    """Tasks (processes *and* threads) the current uid already owns, or 0.

    Linux only, by reading /proc; anywhere else this returns 0 and the caller
    falls back to a flat cap.
    """
    uid = os.getuid()
    total = 0
    try:
        entries = os.listdir("/proc")
    except OSError:
        return 0
    for entry in entries:
        if not entry.isdigit():
            continue
        try:
            if os.stat(f"/proc/{entry}").st_uid != uid:
                continue
            with open(f"/proc/{entry}/status", encoding="utf-8") as fh:
                for line in fh:
                    if line.startswith("Threads:"):
                        total += int(line.split()[1])
                        break
        except (OSError, ValueError):
            continue  # the process went away, or /proc is unreadable
    return total


def nproc_limit(slack: int = TASK_SLACK) -> int:
    """The process cap, expressed as *headroom* rather than an absolute number.

    RLIMIT_NPROC counts every task owned by the real uid — the desktop's
    browser and editor included, not just the sandbox — so a flat 256 does not
    mean "this run may create 256 processes". It means "256 minus whatever the
    machine is already running", and on a workstation with a browser open that
    remainder can be zero. It reached zero here: the ICF harness's single
    `fork()` failed with EAGAIN and the run came back with no results and a
    misleading "the process was killed" for every case.

    Measuring first keeps the control honest — a run may create `slack` tasks,
    whatever else is going on — and keeps it a real fork-bomb stop.
    """
    current = _user_task_count()
    if not current:
        return MIN_TASK_LIMIT
    return max(MIN_TASK_LIMIT, current + slack)


def _preexec(mem_bytes: int, cpu_seconds: int, fsize_bytes: int, tasks: int):
    def apply() -> None:
        # Note: the new session/process group is created by start_new_session=True;
        # don't call os.setsid() here (it would fail — already a session leader).
        if resource is None:
            return
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (fsize_bytes, fsize_bytes))
        # Not every platform/user can set NPROC; the other limits still apply.
        with contextlib.suppress(ValueError, OSError):
            resource.setrlimit(resource.RLIMIT_NPROC, (tasks, tasks))  # anti fork-bomb

    return apply


def read_results(workdir: str) -> dict | None:
    """Parse ``<workdir>/result.json``, or ``None`` if the harness never wrote a
    readable one (crash, kill, OOM, truncated write).

    **This reads a path untrusted code controls**, which is why none of it is a
    plain ``open()``. A submission that does ``os.symlink("/dev/zero",
    "result.json")`` made *this* process — the server, not the sandbox — read
    until it was OOM-killed, and ``os.mkfifo("result.json")`` made it block
    forever, leaking the run directory and the request thread with it. So:
    never follow a symlink, never block on a fifo, only read a regular file,
    and never read more than a result could legitimately be.
    """
    path = os.path.join(workdir, "result.json")
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    try:
        fd = os.open(path, flags)
    except OSError:
        return None  # missing, a symlink, or a fifo with no writer
    try:
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_RESULT_BYTES:
            return None  # a fifo, a directory, a device — or simply too big
        chunks: list[bytes] = []
        remaining = MAX_RESULT_BYTES
        while remaining > 0:
            chunk = os.read(fd, min(remaining, 1 << 20))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
    except OSError:
        return None
    finally:
        os.close(fd)

    try:
        data = json.loads(b"".join(chunks).decode("utf-8", "replace"))
    except ValueError:
        return None
    return data if isinstance(data, dict) else None


def docker_command(workdir: str, limits: Limits, harness_in_container: str,
                   name: str) -> list[str]:
    """The container flags that make the docker backend a real boundary.

    Written once, here, because there are now two callers (the core executor
    and any extension harness) and a flag missing from one of them is a
    silently weaker sandbox.

    ``name`` is not decoration: a `docker run` that times out kills the
    *client*, and the daemon happily keeps running an infinite-loop container
    at its full CPU share forever. The caller kills it by name (see
    :func:`kill_container`).

    The container runs as **this** uid, not as `nobody`. A bind mount has no
    uid mapping, so anything `nobody` created in the run directory — a
    `__pycache__` holding a compiled copy of the submission, say — could not
    be deleted by us afterwards, and `shutil.rmtree(..., ignore_errors=True)`
    silently left it on disk. That breaks the first guarantee in
    docs/code-execution.md: the sandbox is destroyed after the run. Matching
    the uid keeps teardown working and still satisfies "non-root", which the
    guard below enforces rather than assumes.
    """
    uid, gid = os.getuid(), os.getgid()
    if uid == 0:
        raise RuntimeError(
            "refusing to run the docker backend as root — the container would "
            "share that uid with the bind-mounted run directory")
    # The same ceiling RLIMIT_FSIZE gives the subprocess backend. Without it
    # the bind mount is an unbounded write target on the host filesystem, and
    # the in-container degradation ladder can never fire.
    fsize = limits.max_output_kb * 1024 + RESULT_HEADROOM_BYTES
    return [
        "docker", "run", "--rm", "--name", name,
        "--ulimit", f"fsize={fsize}",
        "--network", "none",
        "--memory", f"{limits.memory_limit_mb}m",
        "--memory-swap", f"{limits.memory_limit_mb}m",
        "--cpus", "1",
        "--pids-limit", "128",
        "--cap-drop", "ALL",
        "--security-opt", "no-new-privileges",
        "--read-only",
        # A container-internal tmpfs, not a host path: the rootfs is read-only,
        # so this is the only writable scratch and it dies with the container.
        "--tmpfs", "/tmp:size=16m",  # noqa: S108
        "-v", f"{workdir}:/sandbox:rw",
        "-w", "/sandbox",
        "--user", f"{uid}:{gid}",  # us, so the run directory stays deletable
        settings.DOCKER_IMAGE,
        "python", "-I", harness_in_container, "/sandbox",
    ]


def make_workdir(prefix: str) -> str:
    """A throwaway run directory inside a private parent we own.

    The parent is what keeps a submission private: the leaf holds the
    submitted code, and a run directory sitting directly in a listable
    ``/tmp`` hands it to every local user — along with somewhere to plant a
    ``result.json`` symlink. Under a 0700 parent nobody else can reach the
    leaf at all. ``lstat`` rather than ``stat``, and the uid check, so a
    pre-planted symlink or a squatted directory is refused rather than used.
    """
    root = os.path.join(tempfile.gettempdir(), f"lootcode-runs-{os.getuid()}")
    os.makedirs(root, mode=0o700, exist_ok=True)
    info = os.lstat(root)
    if not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError(f"{root} is not a private directory we own")
    os.chmod(root, 0o700)
    return tempfile.mkdtemp(prefix=prefix, dir=root)


def _destroy(workdir: str) -> None:
    """Remove the run directory, and say so if it survives.

    "Destroyed after the run" is guarantee 1 in docs/code-execution.md, and
    `ignore_errors=True` on its own turns a violation into silence — which is
    how a `__pycache__` owned by the container user sat in /tmp holding a
    compiled copy of someone's submission.
    """
    shutil.rmtree(workdir, ignore_errors=True)
    if os.path.exists(workdir):
        log.warning("sandbox run directory survived teardown: %s", workdir)


def container_name() -> str:
    return f"lootcode-run-{uuid.uuid4().hex}"


def kill_container(name: str) -> None:
    """Stop a container whose client we just timed out. Best effort: if it has
    already exited, `docker kill` fails and there is nothing to clean up."""
    with contextlib.suppress(OSError, subprocess.SubprocessError):
        subprocess.run(["docker", "kill", name],  # noqa: S603, S607
                       capture_output=True, timeout=15, check=False)


def _write_inputs(workdir: str, files: Mapping[str, str], payload: dict) -> None:
    """Materialise a run directory. Names come from the app, never from a user,
    and the containment check keeps it that way if that ever stops being true."""
    root = os.path.realpath(workdir)
    for rel, content in files.items():
        target = os.path.realpath(os.path.join(workdir, rel))
        if not target.startswith(root + os.sep):
            raise ValueError(f"sandbox input escapes the run directory: {rel!r}")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "w", encoding="utf-8") as fh:
            fh.write(content)
    with open(os.path.join(workdir, "payload.json"), "w", encoding="utf-8") as fh:
        json.dump(payload, fh)


def run_harness(*, harness_path: str, files: Mapping[str, str], payload: dict,
                limits: Limits, overall_s: float,
                prefix: str = "lc_run_") -> tuple[dict | None, bool]:
    """Run ``harness_path`` over ``files`` in a throwaway, resource-limited
    sandbox and return ``(parsed result.json | None, timed_out)``.

    ``files`` maps a relative path to its text content; ``payload`` is written
    as payload.json. **The backend is whatever ``EXECUTOR_BACKEND`` says** —
    an operator who turned on `docker` for containment gets it here too, which
    is the whole point of every harness sharing this function.
    """
    if settings.EXECUTOR_BACKEND == "docker":
        return _run_harness_docker(harness_path, files, payload, limits,
                                   overall_s, prefix)
    return _run_harness_subprocess(harness_path, files, payload, limits,
                                   overall_s, prefix)


def _run_harness_docker(harness_path: str, files: Mapping[str, str], payload: dict,
                        limits: Limits, overall_s: float,
                        prefix: str) -> tuple[dict | None, bool]:
    """Same contract, inside a throwaway container: no network, no privileges,
    read-only rootfs, non-root user (see docs/code-execution.md)."""
    workdir = make_workdir(prefix)
    name = container_name()
    try:
        _write_inputs(workdir, files, payload)
        shutil.copy(harness_path, os.path.join(workdir, "harness.py"))
        timed_out = False
        try:
            subprocess.run(  # noqa: S603 - fixed argv, no shell
                docker_command(workdir, limits, "/sandbox/harness.py", name),
                timeout=overall_s + 5, capture_output=True, check=False)
        except subprocess.TimeoutExpired:
            timed_out = True
            kill_container(name)
        return read_results(workdir), timed_out
    finally:
        _destroy(workdir)


def _run_harness_subprocess(harness_path: str, files: Mapping[str, str],
                            payload: dict, limits: Limits, overall_s: float,
                            prefix: str) -> tuple[dict | None, bool]:
    workdir = make_workdir(prefix)
    try:
        _write_inputs(workdir, files, payload)

        cpu_s = int(overall_s) + 1
        mem_bytes = limits.memory_limit_mb * 1024 * 1024
        # The file cap has to fit the whole result.json: the run-wide stdout
        # budget the harness enforces, plus every test's returned value. Sizing
        # it for one test's output made a solution that prints in a loop die
        # mid-write with no results at all.
        fsize_bytes = limits.max_output_kb * 1024 + RESULT_HEADROOM_BYTES
        env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONIOENCODING": "utf-8", "HOME": workdir}

        # Nothing grades on the harness's own stdout/stderr, and *reading*
        # them is a liability: `communicate()` waits for EOF on those pipes,
        # so one `setsid` grandchild that outlives the harness holds the run
        # open for the whole overall budget — one line of user code, one
        # threadpool worker, up to a full timeout. Discard both and wait on
        # the process itself.
        proc = subprocess.Popen(
            [sys.executable, "-I", harness_path, workdir],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            cwd=workdir, env=env, start_new_session=True,
            preexec_fn=(_preexec(mem_bytes, cpu_s, fsize_bytes, nproc_limit())
                        if resource else None),
        )
        timed_out = False
        try:
            proc.wait(timeout=overall_s)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:
            # Always, not only on a timeout: the harness exiting cleanly says
            # nothing about what it forked. Killing the group is what makes
            # "its own disposable sandbox" true for orphans too. Already dead,
            # or not ours to kill — either way, move on and reap.
            with contextlib.suppress(ProcessLookupError, PermissionError):
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            with contextlib.suppress(subprocess.SubprocessError):
                proc.wait(timeout=5)

        return read_results(workdir), timed_out
    finally:
        _destroy(workdir)
