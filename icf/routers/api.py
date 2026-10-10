"""ICF JSON API: start an attempt, run a level, submit a level, autosave.

Grading spawns a sandbox subprocess that can take the better part of a minute
for a full submit, so — exactly as ``app/routers/submissions.py`` does — these
handlers open short sessions around the database work and hold **no** session
across the run itself.
"""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from .. import content, runner, store, views
from ..config import settings
from ..db import session
from ..models import EXAM, PRACTICE

router = APIRouter(prefix="/api/icf")


class StartBody(BaseModel):
    mode: str = EXAM


class CodeBody(BaseModel):
    code: str = Field(max_length=settings.MAX_CODE_CHARS)


class GradeBody(CodeBody):
    level: int = Field(ge=1, le=4)


def _problem_or_404(slug: str):
    problem = content.load(slug)
    if problem is None or content.validate(problem):
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/attempts/{attempt_id}/draft")
def save_draft(attempt_id: str, body: CodeBody, request: Request):
    """Autosave the editor buffer so a reload (or a browser crash) costs nothing."""
    with session() as db:
        attempt = store.get_attempt(db, attempt_id, request.state.user_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="Attempt not found")
        store.save_draft(db, attempt, body.code)
    return {"saved": True}


@router.post("/attempts/{attempt_id}/finish")
def finish(attempt_id: str, request: Request):
    with session() as db:
        attempt = store.get_attempt(db, attempt_id, request.state.user_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="Attempt not found")
        store.finish_attempt(db, attempt)
        problem = _problem_or_404(attempt.slug)
        return {"attempt": views.attempt_payload(attempt, problem)}


@router.get("/attempts/{attempt_id}")
def attempt_state(attempt_id: str, request: Request):
    """Level locks and the remaining clock — the client polls this to stay
    honest about time rather than trusting its own countdown."""
    with session() as db:
        attempt = store.get_attempt(db, attempt_id, request.state.user_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="Attempt not found")
        problem = _problem_or_404(attempt.slug)
        return {"attempt": views.attempt_payload(attempt, problem)}


@router.post("/{slug}/attempts")
def start(slug: str, body: StartBody, request: Request):
    """Start the clock. An already-live attempt is returned instead of a second
    one, so a double-click cannot cost someone their remaining time."""
    problem = _problem_or_404(slug)
    mode = PRACTICE if body.mode == PRACTICE else EXAM
    with session() as db:
        attempt = store.active_attempt(db, request.state.user_id, slug)
        if attempt is None:
            attempt = store.start_attempt(db, request.state.user_id, problem, mode)
        return {"attempt": views.attempt_payload(attempt, problem),
                "code": store.current_code(attempt, problem)}


def _grade(attempt_id: str, body: GradeBody, request: Request, *, mode: str):
    """Shared body of run and submit: check, grade outside any session, record.

    *run* is the fast loop — the current level's visible cases only. *submit* is
    the real thing: levels 1…N, visible and hidden, because level N's
    requirements are cumulative and a regression below must show up.
    """
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Your solution is empty.")

    # 1. read what grading needs, then let the session go.
    with session() as db:
        attempt = store.get_attempt(db, attempt_id, request.state.user_id)
        if attempt is None:
            raise HTTPException(status_code=404, detail="Attempt not found")
        problem = _problem_or_404(attempt.slug)
        if not store.is_unlocked(attempt, body.level):
            raise HTTPException(
                status_code=403,
                detail=f"Level {body.level} is locked — pass level "
                       f"{body.level - 1} first.")
        levels = [body.level] if mode == "run" else list(range(1, body.level + 1))
        store.save_draft(db, attempt, body.code)

    # Tabs to spaces, as the core run API does: mixed indentation is a TabError
    # the solver never sees coming, and 4 spaces is what the editor shows.
    code = body.code.expandtabs(4)

    # 2. grade with no database connection held.
    graded = runner.grade(problem, code, levels, include_hidden=(mode == "submit"))

    # 3. record it and apply it to the attempt.
    with session() as db:
        attempt = store.get_attempt(db, attempt_id, request.state.user_id)
        if attempt is None:  # pragma: no cover - deleted mid-run
            raise HTTPException(status_code=404, detail="Attempt not found")
        outcome = store.record_run(db, attempt, problem, body.level, mode, code,
                                   graded)
        return {
            "mode": mode,
            "level": body.level,
            "late": outcome.late,
            "unlocked_level": outcome.unlocked_level,
            "run": views.run_payload(graded),
            "attempt": views.attempt_payload(attempt, problem),
        }


@router.post("/attempts/{attempt_id}/run")
def run_level(attempt_id: str, body: GradeBody, request: Request):
    return _grade(attempt_id, body, request, mode="run")


@router.post("/attempts/{attempt_id}/submit")
def submit_level(attempt_id: str, body: GradeBody, request: Request):
    return _grade(attempt_id, body, request, mode="submit")
