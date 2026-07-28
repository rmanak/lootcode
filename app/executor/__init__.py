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


@dataclass(frozen=True)
class ProblemView:
    """The exact set of problem attributes the grader reads — the single, shared
    contract between the server and every offline script.

    ``run_submission`` normalizes whatever it is handed through :func:`problem_view`,
    so callers may pass an ORM ``Problem`` row, a ``content.load_problem_dir`` dict,
    or any object exposing these fields — and never a hand-picked subset. When a new
    field is added to the grading contract, it is added HERE (next to the executor
    that reads it) and every caller stays in sync automatically. Frozen so a snapshot
    is safe to hand to worker threads after its DB session has closed."""
    function_name: str
    params: list
    return_type: str
    time_limit_ms: int | None
    memory_limit_mb: int | None
    points: int
    compare: str
    kind: str
    class_name: str | None
    class_methods: list | None


@dataclass(frozen=True)
class CaseView:
    """One test case as the grader reads it — the test-side counterpart to
    :class:`ProblemView`, and frozen for the same reason: a snapshot stays valid
    after the DB session that produced it has closed, so grading can run with no
    connection held.

    Every caller used to build its own: the run endpoint from ORM rows, and the
    admin verify / problem-validation / generator paths from plain dicts, each
    re-deciding what an absent ``weight`` or ``name`` means.

    Named ``CaseView`` rather than ``TestView`` because pytest collects anything
    called ``Test*`` and then errors on the constructor — the ORM's
    ``TestResult`` already has to be import-aliased in the suite for exactly
    that reason, and one such workaround is enough."""
    name: str
    input: dict
    expected: object
    weight: int
    hidden: bool


def _getter(src):  # noqa: ANN001, ANN202 - a `get(key, default)` over either shape
    """Uniform ``get(key, default)`` access to a dict or an object."""
    if isinstance(src, dict):
        return src.get
    return lambda k, d=None: getattr(src, k, d)


def case_views(raw) -> list[CaseView]:
    """Normalize test cases from ORM ``Test`` rows or plain dicts.

    An unnamed test is given a positional name, because the harness keys its
    results by name and two blank names would collide.
    """
    out = []
    for i, t in enumerate(raw):
        if isinstance(t, CaseView):
            out.append(t)
            continue
        get = _getter(t)
        weight = get("weight", 1)
        out.append(CaseView(
            name=get("name") or f"test-{i + 1}",
            input=get("input") or {},
            expected=get("expected"),
            weight=1 if weight is None else weight,
            hidden=bool(get("hidden", False)),
        ))
    return out


def problem_view(src) -> ProblemView:
    """Build a :class:`ProblemView` from an ORM ``Problem``, a content dict, an
    existing view, or any object with the grading fields."""
    if isinstance(src, ProblemView):
        return src
    get = _getter(src)
    return ProblemView(
        function_name=(get("function_name") or "").strip(),
        params=get("params") or [],
        return_type=(get("return_type") or ""),
        time_limit_ms=get("time_limit_ms"),
        memory_limit_mb=get("memory_limit_mb"),
        points=get("points", 100) or 100,
        compare=get("compare", "exact") or "exact",
        kind=get("kind", "function") or "function",
        class_name=get("class_name"),
        class_methods=get("class_methods"),
    )


def run_submission(code: str, problem, tests) -> GradedRun:
    """Grade ``code`` for ``problem`` against ``tests``.

    ``problem`` is any *problem-like* source — an ORM ``Problem`` row (what the
    server passes), a ``content.load_problem_dir`` dict, or a :class:`ProblemView`;
    it is normalized via :func:`problem_view` so no caller maintains its own field
    list. ``tests`` is an iterable of ORM ``Test`` rows, dicts, or
    :class:`CaseView`\\ s, normalized the same way via :func:`case_views`.

    For a class-based "design" problem (``kind == "class"``), ``params`` holds the
    constructor params and ``class_name``/``class_methods`` describe the class the
    harness instantiates and drives through each test's operation sequence."""
    tests = case_views(tests)
    # Forward the full param specs ({name, type}) and the return type so the
    # harness can build/serialize custom types (e.g. TreeNode) at the boundary.
    pv = problem_view(problem)
    limits = Limits(
        time_limit_ms=pv.time_limit_ms or settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=pv.memory_limit_mb or settings.EXEC_MEMORY_LIMIT_MB,
        max_output_kb=settings.EXEC_MAX_OUTPUT_KB,
    )
    specs = [TestSpec(name=t.name, input=t.input) for t in tests]
    outcomes: dict[str, Outcome] = _backend()(
        code, pv.function_name, pv.params, pv.return_type, specs, limits,
        kind=pv.kind, class_name=pv.class_name, class_methods=pv.class_methods,
    )
    compare = pv.compare

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

    score = round(pv.points * earned / total) if total else 0
    return GradedRun(
        results=results, passed_count=passed_count, total_count=len(tests),
        earned_weight=earned, total_weight=total, score=score,
        solved=(len(tests) > 0 and passed_count == len(tests)), runtime_ms=runtime,
    )
