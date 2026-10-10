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

from .base import Limits, Outcome, TestSpec
from .sandbox import container_name, docker_command, kill_container, make_workdir
from .subprocess_executor import build_payload, overall_timeout_s

HARNESS = os.path.join(os.path.dirname(__file__), "harness.py")


def run(code: str, function_name: str, params: list,
        return_type: str, tests: list[TestSpec], limits: Limits,
        *, kind: str = "function", class_name: str | None = None,
        class_methods: list | None = None) -> dict[str, Outcome]:
    workdir = make_workdir("lc_docker_")
    name = container_name()
    try:
        shutil.copy(HARNESS, os.path.join(workdir, "harness.py"))
        with open(os.path.join(workdir, "solution.py"), "w", encoding="utf-8") as f:
            f.write(code)
        # Same payload builder as the subprocess backend: the two backends run
        # the *same* harness, so a divergence here would be a grading difference
        # that depends on EXECUTOR_BACKEND.
        payload = build_payload(code, function_name, params, return_type, tests,
                                limits, kind=kind, class_name=class_name,
                                class_methods=class_methods)
        with open(os.path.join(workdir, "payload.json"), "w", encoding="utf-8") as f:
            json.dump(payload, f)

        overall_s = int(overall_timeout_s(tests, limits))
        # The container flags live in sandbox.py, so the two harnesses that can
        # run here cannot end up with different isolation.
        cmd = docker_command(workdir, limits, "/sandbox/harness.py", name)
        timed_out = False
        try:
            subprocess.run(cmd, timeout=overall_s + 5, capture_output=True)
        except subprocess.TimeoutExpired:
            timed_out = True
            # The client is dead; the container is not. An infinite loop would
            # otherwise keep its CPU share until the daemon restarts.
            kill_container(name)

        return _collect(workdir, tests, timed_out)
    finally:
        shutil.rmtree(workdir, ignore_errors=True)


def _collect(workdir: str, tests: list[TestSpec], timed_out: bool) -> dict[str, Outcome]:
    from .subprocess_executor import _collect as collect  # reuse identical logic

    return collect(workdir, tests, timed_out)
