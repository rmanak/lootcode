"""Code execution facade. Picks a backend and grades a submission.

Public API:
    run_submission(code, problem_like, tests) -> GradedRun
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from ..config import settings
from .base import Limits, Outcome, TestSpec


@dataclass
class TestResult:
    name: str
    hidden: bool
    passed: bool
    status: str          # passed | wrong | timeout | error
    time_ms: float | None
    error: str | None
    stdout: str
    returned: object = None  # actual value (admin verification only; not shown to solvers)


@dataclass
class GradedRun:
    results: list[TestResult]
    passed_count: int
    total_count: int
    earned_weight: int
    total_weight: int
    score: int           # scaled to problem points
    solved: bool
    runtime_ms: float


def _backend():
    if settings.EXECUTOR_BACKEND == "docker":
        from . import docker_executor

        return docker_executor.run
    from . import subprocess_executor

    return subprocess_executor.run


def _jkey(v: object) -> str:
    # Total order over arbitrary JSON values so sorting never raises on mixed types.
    return json.dumps(v, sort_keys=True)


def _normalize(x: object, mode: str) -> object:
    """Canonicalize a value per the problem's comparison mode so that answers the
    statement says are equivalent compare equal."""
    if isinstance(x, list):
        if mode == "unordered":
            return sorted(x, key=_jkey)
        if mode == "set_of_lists":
            return sorted((sorted(e, key=_jkey) if isinstance(e, list) else e for e in x),
                          key=_jkey)
    return x


def _equal(a: object, b: object, mode: str) -> bool:
    # Both values have passed through JSON, so structural == is the right check.
    try:
        return _normalize(a, mode) == _normalize(b, mode)
    except TypeError:
        return a == b


def run_submission(code: str, problem, tests) -> GradedRun:
    """`problem` needs .function_name/.params/.time_limit_ms/.memory_limit_mb/.points;
    `tests` is an iterable of objects with .name/.input/.expected/.weight/.hidden.

    For a class-based "design" problem (`problem.kind == "class"`), `.params` holds
    the constructor params and `.class_name`/`.class_methods` describe the class the
    harness instantiates and drives through each test's operation sequence."""
    tests = list(tests)
    # Forward the full param specs ({name, type}) and the return type so the
    # harness can build/serialize custom types (e.g. TreeNode) at the boundary.
    kind = getattr(problem, "kind", "function") or "function"
    params = problem.params
    return_type = getattr(problem, "return_type", "") or ""
    limits = Limits(
        time_limit_ms=problem.time_limit_ms or settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=problem.memory_limit_mb or settings.EXEC_MEMORY_LIMIT_MB,
        max_output_kb=settings.EXEC_MAX_OUTPUT_KB,
    )
    specs = [TestSpec(name=t.name, input=t.input) for t in tests]
    outcomes: dict[str, Outcome] = _backend()(
        code, problem.function_name, params, return_type, specs, limits,
        kind=kind,
        class_name=getattr(problem, "class_name", None),
        class_methods=getattr(problem, "class_methods", None),
    )
    compare = getattr(problem, "compare", "exact") or "exact"

    results: list[TestResult] = []
    earned = total = passed_count = 0
    runtime = 0.0
    for t in tests:
        total += t.weight
        oc = outcomes.get(t.name) or Outcome(status="error", error="No result.")
        runtime += oc.time_ms or 0
        if oc.status == "ok":
            passed = _equal(oc.returned, t.expected, compare)
            status = "passed" if passed else "wrong"
            error = None if passed else "Wrong answer."
        else:
            passed = False
            status = oc.status  # timeout | error
            error = oc.error
        if passed:
            passed_count += 1
            earned += t.weight
        results.append(TestResult(
            name=t.name, hidden=t.hidden, passed=passed, status=status,
            time_ms=oc.time_ms, error=error, stdout=oc.stdout,
            returned=(oc.returned if oc.status == "ok" else None),
        ))

    points = getattr(problem, "points", 100) or 100
    score = round(points * earned / total) if total else 0
    return GradedRun(
        results=results, passed_count=passed_count, total_count=len(tests),
        earned_weight=earned, total_weight=total, score=score,
        solved=(len(tests) > 0 and passed_count == len(tests)), runtime_ms=runtime,
    )
