"""Run/submit API: execute a solution against all tests and score it."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..db import get_db
from ..executor import run_submission
from ..models import Problem, Submission, TestResult

router = APIRouter(prefix="/api")


class RunBody(BaseModel):
    code: str


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
