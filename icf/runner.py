"""Grade an ICF submission: run authored cases against the solver's class.

Server-side half. It assembles a run directory — the solver's ``solution.py``,
the testkit, and the test modules for the levels being graded — hands it to the
shared sandbox launcher (``app.executor.sandbox``), and turns the harness's
result.json into per-level results.

The sandbox boundary is core's, unchanged: same rlimits, same process group,
same throwaway workdir. What differs from the core executor is only *what* the
harness does inside it — run `@case` functions instead of calling one function
per test — which is why this module exists rather than a new mode in
``app/executor/harness.py``.

**Visible and hidden cases are graded in separate sandbox runs.** Core keeps
hidden tests out of the sandbox entirely (only inputs go in, and the parent
compares); ICF cannot, because its oracle is code. So the split is by run: the
visible run has no hidden module on disk *or* in memory, and the hidden run's
output, messages and timings are discarded here. The oracle is still readable
inside the hidden run's own worker (it is imported there); what the split
removes is any channel wide enough to carry it out — all that escapes a hidden
case is its verdict. See ``icf/docs/security.md``.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.executor.base import Limits
from app.executor.sandbox import run_harness

from .config import settings
from .content import CaseSpec, Problem

HARNESS = Path(__file__).resolve().parent / "sandbox" / "harness.py"
TESTKIT = Path(__file__).resolve().parent / "sandbox" / "testkit.py"

#: Statuses the harness reports, narrowest first.
PASSED, FAILED, TIMEOUT, ERROR = "passed", "failed", "timeout", "error"


@dataclass(frozen=True)
class CaseResult:
    level: int
    hidden: bool
    func: str
    label: str
    status: str
    message: str | None
    time_ms: float
    stdout: str

    @property
    def passed(self) -> bool:
        return self.status == PASSED


@dataclass(frozen=True)
class LevelResult:
    level: int
    title: str
    cases: tuple[CaseResult, ...]

    @property
    def passed_count(self) -> int:
        return sum(1 for c in self.cases if c.passed)

    @property
    def total_count(self) -> int:
        return len(self.cases)

    @property
    def all_passed(self) -> bool:
        return bool(self.cases) and self.passed_count == self.total_count


@dataclass(frozen=True)
class GradedRun:
    levels: tuple[LevelResult, ...]
    load_error: str | None
    runtime_ms: float

    @property
    def passed_count(self) -> int:
        return sum(lv.passed_count for lv in self.levels)

    @property
    def total_count(self) -> int:
        return sum(lv.total_count for lv in self.levels)

    @property
    def all_passed(self) -> bool:
        return bool(self.levels) and all(lv.all_passed for lv in self.levels)

    def level(self, number: int) -> LevelResult | None:
        for lv in self.levels:
            if lv.level == number:
                return lv
        return None


def _clip(text: str, limit: int = settings.MAX_STORED_STDOUT) -> str:
    """Cap captured output, saying so — a silent cut reads like the print broke."""
    notice = "\n... [output truncated]"
    if len(text) <= limit:
        return text
    return text[:limit - len(notice)] + notice


def _payload(problem: Problem, cases: list[CaseSpec]) -> dict:
    per_case_s = problem.case_time_limit_ms / 1000.0
    return {
        "class_name": problem.class_name,
        "import_budget_s": 5.0,
        "max_output_bytes": settings.MAX_OUTPUT_KB * 1024,
        "modules": sorted({c.module for c in cases}),
        "cases": [{"id": c.id, "module": c.module, "func": c.func,
                   "time_limit_s": per_case_s} for c in cases],
    }


def grade(problem: Problem, code: str, levels, *,
          include_hidden: bool = True) -> GradedRun:
    """Run ``code`` against every case for ``levels`` and group the results.

    ``levels`` is the set of levels to grade: a *run* passes just the level the
    solver is working on, a *submit* passes 1…N, because level N's requirements
    are cumulative and a regression in level 1 has to show up.

    Hidden cases, when included, are graded in a **second sandbox run** whose
    messages and captured output are dropped on the way back (see the module
    docstring).
    """
    levels = sorted(levels)
    visible = problem.cases_for(levels, include_hidden=False)
    hidden = [c for c in problem.cases_for(levels, include_hidden=True)
              if c.hidden] if include_hidden else []
    if not visible and not hidden:
        return GradedRun(levels=(), load_error=None, runtime_ms=0.0)

    results: dict[str, dict] = {}
    load_error = None
    runtime = 0.0

    if visible:
        data, timed_out = _launch(problem, code, visible)
        load_error = (data or {}).get("load_error")
        runtime += _harvest(results, visible, data, timed_out, redact=False)

    if hidden:
        data, timed_out = _launch(problem, code, hidden)
        # A hidden run's load_error is a *message*, and a solver can steer what
        # ends up in it (a traceback raised from a line of their choosing while
        # a hidden module imports). Keep the fact, drop the text.
        if load_error is None and (data or {}).get("load_error"):
            load_error = ("Your solution could not be loaded for the hidden "
                          "tests. Run the visible tests to see why.")
        runtime += _harvest(results, hidden, data, timed_out, redact=True)

    return _assemble(problem, [*visible, *hidden], results, load_error, runtime)


def _launch(problem: Problem, code: str, cases: list[CaseSpec]):
    """One sandbox run over ``cases``, with only those cases' modules on disk."""
    files = {"solution.py": code, "icf_testkit.py": TESTKIT.read_text("utf-8")}
    for name in {c.module for c in cases}:
        files[f"{name}.py"] = problem.test_sources[name]

    limits = Limits(
        time_limit_ms=problem.case_time_limit_ms,
        memory_limit_mb=settings.MEMORY_LIMIT_MB,
        max_output_kb=settings.MAX_OUTPUT_KB,
    )
    return run_harness(
        harness_path=str(HARNESS),
        files=files,
        payload=_payload(problem, cases),
        limits=limits,
        overall_s=overall_timeout_s(problem, len(cases), limits),
        prefix="icf_run_",
    )


def overall_timeout_s(problem: Problem, case_count: int, limits: Limits) -> float:
    """Wall-clock ceiling for one sandbox run.

    Every case's own budget plus imports and start-up slack — but capped, so a
    fifty-case suite cannot hold a server thread for the better part of an
    hour. The cap is above any honest run (cases are milliseconds; the per-case
    limit exists for infinite loops) and the harness fails closed when it is
    hit: unreported cases come back as timeouts, never passes.
    """
    per_case_s = limits.time_limit_ms / 1000.0
    wanted = limits.import_budget_s + per_case_s * case_count + 5.0
    return min(wanted, settings.MAX_RUN_SECONDS)


_FALLBACK_MESSAGE = ("The run was stopped (overall time limit, or the process "
                     "was killed — possible memory limit or crash).")


def _harvest(into: dict[str, dict], cases: list[CaseSpec], data: dict | None,
             timed_out: bool, *, redact: bool) -> float:
    """Fold one sandbox run's result.json into ``into``, keyed by case id.

    Defensive about shape: result.json is written inside the sandbox, so a
    missing, malformed or hostile entry has to grade as a failure rather than
    raise out of the request.
    """
    reported: dict[str, dict] = {}
    for entry in (data or {}).get("results", []):
        if isinstance(entry, dict) and isinstance(entry.get("id"), str):
            reported[entry["id"]] = entry

    runtime = 0.0
    for spec in cases:
        raw = reported.get(spec.id)
        if raw is None:
            into[spec.id] = {"status": TIMEOUT if timed_out else ERROR,
                             "message": _FALLBACK_MESSAGE, "time_ms": 0,
                             "stdout": ""}
            continue
        time_ms = raw.get("time_ms")
        time_ms = float(time_ms) if isinstance(time_ms, int | float) else 0.0
        if not redact:
            runtime += time_ms
        status = raw.get("status")
        into[spec.id] = {
            "status": status if status in (PASSED, FAILED, TIMEOUT, ERROR) else ERROR,
            # Redacted runs keep the verdict and nothing else: a hidden case
            # reveals pass/fail by design, and must reveal nothing more even if
            # a future route starts rendering these fields. Timing included —
            # a solver who can read the oracle out of the worker's memory could
            # otherwise spell it back out one `sleep` at a time.
            "message": None if redact else raw.get("message"),
            "time_ms": 0.0 if redact else time_ms,
            "stdout": "" if redact else _clip(raw.get("stdout") or ""),
        }
    return runtime


def _assemble(problem: Problem, cases: list[CaseSpec], results: dict[str, dict],
              load_error: str | None, runtime: float) -> GradedRun:
    """Group the collected case results by level, in level then authored order."""
    grouped: dict[int, list[CaseResult]] = {}
    for spec in sorted(cases, key=lambda c: (c.level, c.hidden)):
        raw = results.get(spec.id, {"status": ERROR, "message": _FALLBACK_MESSAGE,
                                    "time_ms": 0, "stdout": ""})
        grouped.setdefault(spec.level, []).append(CaseResult(
            level=spec.level, hidden=spec.hidden, func=spec.func, label=spec.label,
            status=raw["status"], message=raw["message"],
            time_ms=round(raw["time_ms"], 2), stdout=raw["stdout"],
        ))

    levels = tuple(
        LevelResult(level=number, title=problem.level(number).title,
                    cases=tuple(results_for))
        for number, results_for in sorted(grouped.items()))
    return GradedRun(levels=levels, load_error=load_error,
                     runtime_ms=round(runtime, 1))
