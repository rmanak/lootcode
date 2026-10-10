"""ICF pages: the problem list, the workspace, and an attempt report."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.templating import templates

from .. import content, store, views
from ..db import get_db
from ..models import EXAM

router = APIRouter(prefix="/icf")


@router.get("")
def index(request: Request, db: Session = Depends(get_db)):
    """Every ICF problem, with this solver's best result on each."""
    problems = content.load_all()
    best: dict[str, dict] = {}
    for attempt in store.user_attempts(db, request.state.user_id, limit=200):
        row = best.setdefault(attempt.slug, {"level": 0, "attempts": 0,
                                             "active": None})
        row["attempts"] += 1
        row["level"] = max(row["level"], attempt.highest_level_passed)
        if attempt.status == "active" and row["active"] is None:
            row["active"] = attempt
    return templates.TemplateResponse(request, "icf/index.html", {
        "problems": problems,
        "best": best,
    })


@router.get("/attempts/{attempt_id}")
def report(attempt_id: str, request: Request, db: Session = Depends(get_db)):
    """What happened in one sitting: levels reached, clock used, run history."""
    attempt = store.get_attempt(db, attempt_id, request.state.user_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Attempt not found")
    problem = content.load(attempt.slug)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return templates.TemplateResponse(request, "icf/report.html", {
        "problem": problem,
        "attempt": attempt,
        "state": views.attempt_payload(attempt, problem),
        "score": views.score(attempt, problem),
        "runs": list(reversed(attempt.runs)),
        "tz": views.viewer_tz(request),
        "elapsed_s": store.elapsed_seconds(attempt),
    })


@router.get("/{slug}")
def workspace(slug: str, request: Request, db: Session = Depends(get_db)):
    """The assessment itself. Resumes a live attempt; otherwise offers to start
    one — the clock must not start just because someone opened the page."""
    problem = content.load(slug)
    if problem is None or content.validate(problem):
        raise HTTPException(status_code=404, detail="Problem not found")
    attempt = store.active_attempt(db, request.state.user_id, slug)
    state = views.attempt_payload(attempt, problem) if attempt else None
    return templates.TemplateResponse(request, "icf/workspace.html", {
        "problem": problem,
        "attempt": attempt,
        "state": state,
        "code": store.current_code(attempt, problem) if attempt
        else problem.starter_code,
        "past_attempts": store.user_attempts(db, request.state.user_id, slug,
                                             limit=10),
        "tz": views.viewer_tz(request),
        "default_mode": EXAM,
    })
