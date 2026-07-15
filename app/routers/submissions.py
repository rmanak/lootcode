"""Run/submit API: execute a solution against all tests and score it."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import store
from ..config import settings
from ..db import get_db
from ..executor import run_submission
from ..models import Problem, Submission, TestResult

router = APIRouter(prefix="/api")


class RunBody(BaseModel):
    code: str


class KnownBody(BaseModel):
    known: bool


class VisitLaterBody(BaseModel):
    visit_later: bool


@router.post("/problems/{slug}/run")
def run(slug: str, body: RunBody, request: Request, db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Your solution is empty.")

    # Normalize tabs to spaces so mixed tab/space indentation can't raise a
    # Python TabError. expandtabs(4) matches the editor's 4-space tab stops, so
    # the executed (and stored) code lines up with what the user saw on screen.
    code = body.code.expandtabs(4)

    graded = run_submission(code, prob, prob.tests)

    sub = Submission(
        user_id=request.state.user_id, problem_id=prob.id, code=code,
        status="done", score=graded.score, passed_count=graded.passed_count,
        total_count=graded.total_count, runtime_ms=int(graded.runtime_ms),
    )
    db.add(sub)
    db.flush()

    out, hidden_i, visible_i = [], 0, 0
    for r in graded.results:
        db.add(TestResult(
            submission_id=sub.id, name=r.name, hidden=r.hidden, passed=r.passed,
            status=r.status, time_ms=int(r.time_ms or 0), error=r.error, stdout=r.stdout,
        ))
        if r.hidden:
            hidden_i += 1
            # Hidden tests: reveal pass/fail only — never the input/expected/output.
            out.append({"label": f"Hidden test {hidden_i}", "hidden": True,
                        "passed": r.passed, "status": r.status})
        else:
            visible_i += 1
            out.append({"label": r.name, "hidden": False, "passed": r.passed,
                        "status": r.status, "time_ms": round(r.time_ms or 0, 1),
                        "error": r.error, "stdout": (r.stdout or "")[:4000]})
    db.commit()

    return {
        "score": graded.score, "points": prob.points,
        "passed_count": graded.passed_count, "total_count": graded.total_count,
        "solved": graded.solved, "runtime_ms": round(graded.runtime_ms, 1),
        "results": out,
    }


@router.post("/problems/{slug}/known")
def set_known(slug: str, body: KnownBody, request: Request,
              db: Session = Depends(get_db)):
    """Mark/unmark this problem as "known" for the current user. Known problems
    are hidden from the random "next" picks and the "unknown only" filter."""
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    known = store.set_problem_known(db, request.state.user_id, prob.id, body.known)
    return {"known": known}


@router.post("/problems/{slug}/visit-later")
def set_visit_later(slug: str, body: VisitLaterBody, request: Request,
                    db: Session = Depends(get_db)):
    """Flag/unflag this problem as "visit later" for the current user — a personal
    bookmark surfaced by the "Visit later" filter on the problem list."""
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    visit_later = store.set_problem_visit_later(
        db, request.state.user_id, prob.id, body.visit_later)
    return {"visit_later": visit_later}


def _sse(payload: dict) -> str:
    """Encode one Server-Sent Events frame (a single JSON ``data:`` line)."""
    return f"data: {json.dumps(payload)}\n\n"


@router.post("/problems/{slug}/help")
def ai_help(slug: str, request: Request, db: Session = Depends(get_db)):
    """Stream one extra, more-concrete "Get More Help with AI" hint.

    Generated live from the problem title + statement + existing hints, so it
    doesn't repeat what the user has already read. Streamed as Server-Sent Events
    (``{"type": "delta"|"error"|"done", ...}``) so the UI can render it token by
    token and show progress. Enabled only when the startup probe found a reachable
    OpenAI-compatible endpoint (see app/llm/help_generator.py).
    """
    if not settings.llm_help_available:
        raise HTTPException(status_code=503, detail="AI help is not configured.")
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    # Snapshot everything the generator needs BEFORE returning: the DB session is
    # torn down when this function returns, but the stream body runs afterwards, so
    # it must not touch the ORM.
    title = prob.title
    statement = prob.statement_md or ""
    hints = list(prob.hints or [])

    from ..llm.help_generator import stream_help

    def event_stream():
        got_any = False
        try:
            for piece in stream_help(title, statement, hints):
                got_any = True
                yield _sse({"type": "delta", "text": piece})
        except Exception as exc:  # noqa: BLE001 - report failure to the client cleanly
            yield _sse({"type": "error", "message": f"AI help failed: {exc}"})
            return
        if not got_any:
            yield _sse({"type": "error", "message": "The AI returned an empty response."})
        else:
            yield _sse({"type": "done"})

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        # Defeat proxy/browser buffering so chunks arrive as they're produced.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
