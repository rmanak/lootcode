"""Docker executor backend: stronger isolation for untrusted code.

Runs the same harness inside a throwaway container with no network, dropped
privileges, a read-only root, capped memory/CPU/PIDs, and a non-root user.
Requires Docker and an image with Python 3 (build from infra/runner.Dockerfile,
tagged `lootcode-runner` by default — see docs/code-execution.md).

Selected via EXECUTOR_BACKEND=docker. Falls back is the caller's concern; this
module just raises if Docker is unavailable.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile

from ..config import settings
from .base import Limits, Outcome, TestSpec

HARNESS = os.path.join(os.path.dirname(__file__), "harness.py")


def run(code: str, function_name: str, params: list,
        return_type: str, tests: list[TestSpec], limits: Limits) -> dict[str, Outcome]:
    workdir = tempfile.mkdtemp(prefix="lc_docker_")
    per_test_s = limits.time_limit_ms / 1000.0
    try:
        shutil.copy(HARNESS, os.path.join(workdir, "harness.py"))
        with open(os.path.join(workdir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)
        payload = {
            "function_name": function_name, "params": params,
            "return_type": return_type,
            "import_budget_s": limits.import_budget_s,
            "max_output_bytes": limits.max_output_kb * 1024,
            "tests": [{"name": t.name, "input": t.input, "time_limit_s": per_test_s}
                      for t in tests],
        }
        with open(os.path.join(workdir, "payload.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f)

        overall_s = int(limits.import_budget_s + per_test_s * len(tests) + 5.0)
        cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", f"{limits.memory_limit_mb}m",
            "--memory-swap", f"{limits.memory_limit_mb}m",
            "--cpus", "1",
            "--pids-limit", "128",
            "--cap-drop", "ALL",
            "--security-opt", "no-new-privileges",
            "--read-only",
            "--tmpfs", "/tmp:size=16m",
            "-v", f"{workdir}:/sandbox:rw",
            "-w", "/sandbox",
            "--user", "65534:65534",  # nobody
            settings.DOCKER_IMAGE,
            "python", "-I", "/sandbox/harness.py", "/sandbox",
        ]
        timed_out = False
        try:
            subprocess.run(cmd, timeout=overall_s + 5, capture_output=True)
        except subprocess.TimeoutExpired:
            timed_out = True

        return _collect(workdir, tests, timed_out)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _collect(workdir: str, tests: list[TestSpec], timed_out: bool) -> dict[str, Outcome]:
    from .subprocess_executor import _collect as collect  # reuse identical logic

    return collect(workdir, tests, timed_out)
