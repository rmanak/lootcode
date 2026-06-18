"""Default executor backend: run untrusted code in a resource-limited subprocess.

Guarantees (see docs/code-execution.md): per-test CPU/wall-time limits, an
address-space (memory) cap, a process cap (anti fork-bomb), a file-size cap, a
minimal environment with no secrets, its own process group (killed on timeout),
and a throwaway working directory deleted afterwards.

NOTE: a subprocess does NOT block network access. For untrusted multi-user
deployments use the `docker` backend. This backend suits a personal/home
instance and is the zero-dependency default.
"""
from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile

from .base import Limits, Outcome, TestSpec

HARNESS = os.path.join(os.path.dirname(__file__), "harness.py")

try:
    import resource  # POSIX only
except ImportError:  # pragma: no cover - Windows fallback
    resource = None


def _preexec(mem_bytes: int, cpu_seconds: int, fsize_bytes: int):
    def apply() -> None:
        # Note: the new session/process group is created by start_new_session=True;
        # don't call os.setsid() here (it would fail — already a session leader).
        if resource is None:
            return
        resource.setrlimit(resource.RLIMIT_AS, (mem_bytes, mem_bytes))
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
        resource.setrlimit(resource.RLIMIT_FSIZE, (fsize_bytes, fsize_bytes))
        try:
            resource.setrlimit(resource.RLIMIT_NPROC, (256, 256))  # anti fork-bomb
        except (ValueError, OSError):
            pass

    return apply


def run(code: str, function_name: str, params: list[str],
        tests: list[TestSpec], limits: Limits) -> dict[str, Outcome]:
    workdir = tempfile.mkdtemp(prefix="lc_run_")
    per_test_s = limits.time_limit_ms / 1000.0
    try:
        with open(os.path.join(workdir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)
        payload = {
            "function_name": function_name,
            "params": params,
            "import_budget_s": limits.import_budget_s,
            "max_output_bytes": limits.max_output_kb * 1024,
            "tests": [{"name": t.name, "input": t.input, "time_limit_s": per_test_s}
                      for t in tests],
        }
        with open(os.path.join(workdir, "payload.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f)

        overall_s = limits.import_budget_s + per_test_s * len(tests) + 5.0
        cpu_s = int(overall_s) + 1
        mem_bytes = limits.memory_limit_mb * 1024 * 1024
        env = {"PATH": "/usr/bin:/bin", "PYTHONDONTWRITEBYTECODE": "1",
               "PYTHONIOENCODING": "utf-8", "HOME": workdir}

        proc = subprocess.Popen(
            [sys.executable, "-I", HARNESS, workdir],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=workdir, env=env, start_new_session=True,
            preexec_fn=_preexec(mem_bytes, cpu_s, limits.max_output_kb * 1024 + 4096)
            if resource else None,
        )
        timed_out = False
        try:
            proc.communicate(timeout=overall_s)
        except subprocess.TimeoutExpired:
            timed_out = True
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except (ProcessLookupError, PermissionError):
                pass
            proc.communicate()

        return _collect(workdir, tests, timed_out)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _collect(workdir: str, tests: list[TestSpec], timed_out: bool) -> dict[str, Outcome]:
    result_path = os.path.join(workdir, "result.json")
    by_name: dict[str, Outcome] = {}
    if os.path.exists(result_path):
        try:
            data = json.load(open(result_path, encoding="utf-8"))
            for r in data.get("results", []):
                by_name[r["name"]] = Outcome.from_dict(r)
        except (ValueError, OSError):
            pass

    # Fill in any test the harness didn't report (crash / kill / OOM / timeout).
    fallback_status = "timeout" if timed_out else "error"
    fallback_error = ("The run was stopped (overall time limit or the process was "
                      "killed — possible memory limit or crash).")
    for t in tests:
        if t.name not in by_name:
            by_name[t.name] = Outcome(status=fallback_status, error=fallback_error)
    return by_name
