"""Default executor backend: run untrusted code in a resource-limited subprocess.

The process-level guarantees — rlimits, own process group, minimal environment,
throwaway workdir — live in `sandbox.py`, which is shared with every other
harness in the tree. This module is the problem-grading half: build the payload
`harness.py` expects, and turn its result.json back into `Outcome`s.

NOTE: a subprocess does NOT block network access. For untrusted multi-user
deployments use the `docker` backend. This backend suits a personal/home
instance and is the zero-dependency default.
"""
from __future__ import annotations

import os

from . import sandbox
from .base import Limits, Outcome, TestSpec

HARNESS = os.path.join(os.path.dirname(__file__), "harness.py")


def build_payload(code: str, function_name: str, params: list, return_type: str,
                  tests: list[TestSpec], limits: Limits, *, kind: str,
                  class_name: str | None, class_methods: list | None) -> dict:
    """What `harness.py` reads out of payload.json. Shared with the docker
    backend so the two can never drift into grading differently."""
    per_test_s = limits.time_limit_ms / 1000.0
    return {
        "kind": kind,
        "function_name": function_name,
        "params": params,
        "return_type": return_type,
        "class_name": class_name,
        "class_methods": class_methods,
        "import_budget_s": limits.import_budget_s,
        "max_output_bytes": limits.max_output_kb * 1024,
        "tests": [{"name": t.name, "input": t.input, "time_limit_s": per_test_s}
                  for t in tests],
    }


def overall_timeout_s(tests: list[TestSpec], limits: Limits) -> float:
    """Wall-clock budget for the whole harness process: every test's own limit,
    plus the import budget, plus slack for start-up and writing results."""
    return limits.import_budget_s + (limits.time_limit_ms / 1000.0) * len(tests) + 5.0


def run(code: str, function_name: str, params: list,
        return_type: str, tests: list[TestSpec], limits: Limits,
        *, kind: str = "function", class_name: str | None = None,
        class_methods: list | None = None) -> dict[str, Outcome]:
    data, timed_out = sandbox.run_harness(
        harness_path=HARNESS,
        files={"solution.py": code},
        payload=build_payload(code, function_name, params, return_type, tests,
                              limits, kind=kind, class_name=class_name,
                              class_methods=class_methods),
        limits=limits,
        overall_s=overall_timeout_s(tests, limits),
    )
    return outcomes(data, tests, timed_out)


def outcomes(data: dict | None, tests: list[TestSpec],
             timed_out: bool) -> dict[str, Outcome]:
    """Map a harness result.json onto one `Outcome` per requested test.

    result.json is written *inside* the sandbox, so its shape is untrusted:
    an entry that is not a dict with a string name is dropped, and the test it
    should have covered falls through to the error fallback below rather than
    raising out of the request.
    """
    by_name: dict[str, Outcome] = {}
    for r in (data or {}).get("results", []):
        if isinstance(r, dict) and isinstance(r.get("name"), str):
            by_name[r["name"]] = Outcome.from_dict(r)

    # Fill in any test the harness didn't report (crash / kill / OOM / timeout).
    fallback_status = "timeout" if timed_out else "error"
    fallback_error = ("The run was stopped (overall time limit or the process was "
                      "killed — possible memory limit or crash).")
    for t in tests:
        if t.name not in by_name:
            by_name[t.name] = Outcome(status=fallback_status, error=fallback_error)
    return by_name


def _collect(workdir: str, tests: list[TestSpec], timed_out: bool) -> dict[str, Outcome]:
    """Read a finished workdir and grade it. Used by the docker backend, which
    owns its own container lifecycle but writes the same result.json."""
    return outcomes(sandbox.read_results(workdir), tests, timed_out)
