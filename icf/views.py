"""Shaping ICF state for the browser — and deciding what a solver may see.

The redaction rule lives here, in one place, so no route can leak it by
accident: a **hidden** case reports pass/fail and nothing else. No label, no
assertion message, no captured output, not even its name.
"""
from __future__ import annotations

from .content import Problem
from .models import Attempt
from .runner import GradedRun, LevelResult
from .store import elapsed_seconds, level_state, remaining_ms


def attempt_payload(attempt: Attempt, problem: Problem) -> dict:
    """Everything the workspace needs to render the clock and the level pills."""
    return {
        "id": attempt.id,
        "slug": attempt.slug,
        "mode": attempt.mode,
        "status": attempt.status,
        "remaining_ms": remaining_ms(attempt),
        "elapsed_s": elapsed_seconds(attempt),
        "time_cap_minutes": problem.time_cap_minutes,
        "highest_level_passed": attempt.highest_level_passed,
        "levels": [level_payload(attempt, problem, lv.number) for lv in problem.levels],
    }


def level_payload(attempt: Attempt, problem: Problem, number: int) -> dict:
    state = level_state(attempt, number)
    level = problem.level(number)
    return {
        "level": number,
        "title": level.title,
        "points": level.points,
        "unlocked": bool(state and state.unlocked),
        "passed": bool(state and state.passed),
        "best_passed": state.best_passed if state else 0,
        "best_total": state.best_total if state else 0,
        "visible_count": len(level.visible_cases),
        "hidden_count": len(level.hidden_cases),
    }


def case_payload(case, hidden_index: int) -> dict:
    """One case result. Hidden cases are reduced to a number and a verdict."""
    if case.hidden:
        return {
            "hidden": True,
            "label": f"Hidden test {hidden_index}",
            "status": case.status,
            "passed": case.passed,
        }
    return {
        "hidden": False,
        "name": case.func,
        "label": case.label,
        "status": case.status,
        "passed": case.passed,
        "message": case.message,
        "time_ms": case.time_ms,
        "stdout": case.stdout,
    }


def level_result_payload(result: LevelResult) -> dict:
    cases, hidden_index = [], 0
    for case in result.cases:
        if case.hidden:
            hidden_index += 1
        cases.append(case_payload(case, hidden_index))
    return {
        "level": result.level,
        "title": result.title,
        "passed_count": result.passed_count,
        "total_count": result.total_count,
        "all_passed": result.all_passed,
        "cases": cases,
    }


def run_payload(graded: GradedRun) -> dict:
    return {
        "passed_count": graded.passed_count,
        "total_count": graded.total_count,
        "all_passed": graded.all_passed,
        "runtime_ms": graded.runtime_ms,
        "load_error": graded.load_error,
        "levels": [level_result_payload(lv) for lv in graded.levels],
    }


def score(attempt: Attempt, problem: Problem) -> int:
    """Points earned: whole levels only, which is what the format measures."""
    return sum(lv.points for lv in problem.levels
               if lv.number <= attempt.highest_level_passed)


def viewer_tz(request):
    """The visitor's timezone from core's ``lc_tz`` cookie, falling back to UTC.

    Core sets that cookie in ``base.html`` and reads it the same way in
    ``app/routers/pages.py``; the value arrives percent-encoded, which is why
    it is unquoted here before ``ZoneInfo`` sees it.
    """
    from urllib.parse import unquote
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

    name = request.cookies.get("lc_tz")
    if name:
        try:
            return ZoneInfo(unquote(name))
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return ZoneInfo("UTC")
