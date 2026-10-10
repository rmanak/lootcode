"""Run/submit API: execute a solution against all tests and score it."""
from __future__ import annotations

import json
import threading
import time

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import store
from ..config import settings
from ..db import SessionLocal, get_db
from ..executor import case_views, problem_view, run_submission
from ..logging_config import get_logger
from ..models import Problem, Submission, TestResult

log = get_logger(__name__)

router = APIRouter(prefix="/api")


# Submitted code is stored verbatim on every attempt, so it needs a ceiling: a
# solution to any problem in the bank is a few KB, and 256 KB is a generous
# multiple of that. Enforced by pydantic, so an oversized body is a 422 rather
# than a row in the database.
MAX_CODE_CHARS = 256 * 1024

# Captured stdout was capped at 4,000 chars on the way *out* to the browser but
# stored uncapped, so a print-in-a-loop solution wrote megabytes per test into
# SQLite while showing the user 4,000 characters. Now the cap is applied once, on
# the way in.
MAX_STORED_STDOUT = 4000


_STDOUT_CLIPPED = "\n... [output truncated]"


def _clip_stdout(text: str) -> str:
    """Cap captured output, saying so — a silent cut reads like the print stopped
    working. The notice fits *inside* MAX_STORED_STDOUT so the cap stays a hard
    bound. (The sandbox applies its own, larger run-wide budget first.)"""
    if len(text) <= MAX_STORED_STDOUT:
        return text
    return text[:MAX_STORED_STDOUT - len(_STDOUT_CLIPPED)] + _STDOUT_CLIPPED


class RunBody(BaseModel):
    code: str = Field(max_length=MAX_CODE_CHARS)


class KnownBody(BaseModel):
    known: bool


class VisitLaterBody(BaseModel):
    visit_later: bool


@router.post("/problems/{slug}/run")
def run(slug: str, body: RunBody, request: Request):
    """Grade a submission and record it.

    Deliberately **not** on ``Depends(get_db)``. Grading spawns a sandbox
    subprocess and can take the full time limit (~15 s for a suite); holding a
    session open across it kept a SQLite connection — and, under the default
    journal mode, a lock — checked out for the whole run. Three short sessions
    instead: read the problem, grade with nothing checked out, then write.
    """
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Your solution is empty.")

    # --- 1. read what grading needs, then let the session go ----------------
    with SessionLocal() as db:
        prob = db.scalar(select(Problem).where(Problem.slug == slug))
        if prob is None:
            raise HTTPException(status_code=404, detail="Problem not found")
        problem_id, points = prob.id, prob.points
        # Both views are frozen precisely so they can outlive this session.
        view = problem_view(prob)
        tests = case_views(prob.tests)

    # Normalize tabs to spaces so mixed tab/space indentation can't raise a
    # Python TabError. expandtabs(4) matches the editor's 4-space tab stops, so
    # the executed (and stored) code lines up with what the user saw on screen.
    code = body.code.expandtabs(4)

    # --- 2. grade with no database connection held --------------------------
    graded = run_submission(code, view, tests)

    # --- 3. record it -------------------------------------------------------
    out, hidden_i, visible_i = [], 0, 0
    with SessionLocal() as db:
        sub = Submission(
            user_id=request.state.user_id, problem_id=problem_id, code=code,
            status="done", score=graded.score, passed_count=graded.passed_count,
            total_count=graded.total_count, runtime_ms=int(graded.runtime_ms),
        )
        db.add(sub)
        db.flush()

        for r in graded.results:
            stdout = _clip_stdout(r.stdout or "")
            db.add(TestResult(
                submission_id=sub.id, name=r.name, hidden=r.hidden, passed=r.passed,
                status=r.status, time_ms=int(r.time_ms or 0), error=r.error,
                stdout=stdout,
            ))
            if r.hidden:
                hidden_i += 1
                # Hidden tests: reveal pass/fail only — never input/expected/output.
                out.append({"label": f"Hidden test {hidden_i}", "hidden": True,
                            "passed": r.passed, "status": r.status})
            else:
                visible_i += 1
                out.append({"label": r.name, "hidden": False, "passed": r.passed,
                            "status": r.status, "time_ms": round(r.time_ms or 0, 1),
                            "error": r.error, "stdout": stdout})
        db.commit()

    if not graded.solved:
        log.info("run %s: %d/%d tests passed", slug,
                 graded.passed_count, graded.total_count)

    return {
        "score": graded.score, "points": points,
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


# This route is unauthenticated and flips a process-wide flag that gates the
# admin LLM routes (settings.generation_enabled), and each call makes an outbound
# HTTP request. One re-probe every few seconds is all a human clicking a button
# needs; anything faster is a loop.
_REFRESH_MIN_INTERVAL_S = 3.0
_last_refresh = {"at": 0.0, "result": None}


@router.post("/llm/refresh")
def refresh_llm():
    """Re-probe the optional LLM endpoint now and report what it enables.

    The background watcher (``help_generator.watch_availability``) re-probes on
    its own every ``LLM_HELP_PROBE_INTERVAL`` seconds; this is the immediate,
    manual version behind the admin page's "re-check" button — and the only one
    when that interval is 0. On success the page reloads with the features on.

    Throttled: within ``_REFRESH_MIN_INTERVAL_S`` the previous answer is replayed
    rather than re-probed, so this can't be used to hammer the LLM endpoint or to
    flip the global flag in a tight loop.
    """
    from ..llm.help_generator import refresh_availability

    now = time.monotonic()
    if _last_refresh["result"] is not None and \
            now - _last_refresh["at"] < _REFRESH_MIN_INTERVAL_S:
        return _last_refresh["result"]

    available = refresh_availability()
    result = {
        "available": available,
        "endpoint": settings.LLM_HELP_URL,
        "ai_help_enabled": settings.llm_help_available,
        "generation_enabled": settings.generation_enabled,
    }
    _last_refresh.update(at=now, result=result)
    log.info("LLM endpoint re-probed: %s",
             "available" if available else "unavailable")
    return result


@router.get("/llm/status")
def llm_status():
    """What the optional LLM endpoint currently enables, as last probed.

    Reads the cached flag that the background watcher keeps current
    (``help_generator.watch_availability``) and makes no outbound request, so
    the problem page can poll it to switch "Get More Help with AI" and
    "Analysis" on and off live as the LLM server comes and goes.
    """
    return {
        "available": settings.llm_help_available,
        "ai_help_enabled": settings.llm_help_available,
        "generation_enabled": settings.generation_enabled,
    }


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

    return _sse_response(event_stream())


def _sse_response(events) -> StreamingResponse:
    return StreamingResponse(
        events,
        media_type="text/event-stream",
        # Defeat proxy/browser buffering so chunks arrive as they're produced.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# The whole solution goes into the prompt. RunBody's 256 KB ceiling is about
# storage; a model's context is far smaller, and no real solution is this long.
MAX_ANALYSIS_CODE_CHARS = 20_000

# Throttle for `progress` frames — one per streamed token is wasted bytes.
_PROGRESS_EVERY_S = 0.2

# Each analysis is a sandbox run plus an LLM stream that can hold a threadpool
# thread for minutes against a busy model. The route is unauthenticated, so cap
# how many run at once; a request over the cap is told to retry, never queued.
_ANALYSES = threading.BoundedSemaphore(2)


@router.post("/problems/{slug}/analyze")
def analyze(slug: str, body: RunBody):
    """Stream an AI "Analysis" of a solution: Approach, Efficiency, Code Style.

    The code is graded first, through the same ``run_submission`` path as
    ``/run`` — the model is told the real verdict, not asked to guess it — but
    nothing is recorded: analysing is not an attempt. Then the optional LLM
    endpoint writes a schema-constrained report (app/llm/solution_analyzer.py).

    Server-Sent Events, ``{"type": ...}``:
      ``status``   a progress message;
      ``verdict``  ``{status, passed, total}`` once grading is done;
      ``progress`` ``{chars, pillars}`` while the report streams — characters so
                   far and how many pillars are complete;
      ``result``   ``{analysis}``, the normalised report; then ``done``;
      ``error``    ``{message}`` — terminal.

    Like ``/run`` it holds no database session while grading or generating.
    """
    if not settings.llm_help_available:
        raise HTTPException(status_code=503, detail="AI analysis is not configured.")
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="Your solution is empty.")
    code = body.code.expandtabs(4)  # as /run does, so the verdict matches it
    # Measured after expandtabs: a tab-padded body would otherwise grow 4x past it.
    if len(code) > MAX_ANALYSIS_CODE_CHARS:
        raise HTTPException(status_code=400,
                            detail="This solution is too long to analyse.")

    from ..llm import solution_analyzer as analyzer

    with SessionLocal() as db:
        prob = db.scalar(select(Problem).where(Problem.slug == slug))
        if prob is None:
            raise HTTPException(status_code=404, detail="Problem not found")
        view = problem_view(prob)
        tests = case_views(prob.tests)
        title, statement = prob.title, prob.statement_md or ""
        reference = prob.canonical_solution or ""
        signature = analyzer.signature(prob)
        starter = (prob.starter_code or "").expandtabs(4).strip()

    if code.strip() == starter:
        raise HTTPException(status_code=400,
                            detail="Write a solution first — this is still the starter code.")

    def event_stream():
        # Acquired inside the generator so the `finally` always releases it — a
        # body that is never iterated never takes a slot.
        if not _ANALYSES.acquire(blocking=False):
            yield _sse({"type": "error", "message":
                        "Other analyses are running — try again in a moment."})
            return
        try:
            yield from analysis_events()
        finally:
            _ANALYSES.release()

    def analysis_events():
        yield _sse({"type": "status", "message": "Running your code against the tests…"})
        try:
            graded = run_submission(code, view, tests)
            verdict = analyzer.build_verdict(graded, tests)
            prompt = analyzer.render_prompt(
                title=title, statement=statement, signature=signature,
                reference=reference, code=code, verdict=verdict)
        except Exception:  # noqa: BLE001 - details go to the log, not the page
            log.exception("analyze %s: grading failed", slug)
            yield _sse({"type": "error", "message": "Could not run your code."})
            return
        yield _sse({"type": "verdict", "status": verdict.status,
                    "passed": verdict.passed, "total": verdict.total})
        if len(prompt) > analyzer.MAX_PROMPT_CHARS:
            log.warning("analyze %s: prompt of %d chars refused", slug, len(prompt))
            yield _sse({"type": "error", "message":
                        "This solution is too long to analyse."})
            return
        yield _sse({"type": "status", "message": "Analyzing your solution…"})

        text, last = "", 0.0
        try:
            for piece in analyzer.stream_analysis(prompt):
                text += piece
                now = time.monotonic()
                if now - last >= _PROGRESS_EVERY_S:
                    last = now
                    yield _sse({"type": "progress", "chars": len(text),
                                "pillars": analyzer.pillars_done(text)})
            analysis = analyzer.parse_analysis(text)
        except Exception as exc:  # noqa: BLE001 - report failure to the client cleanly
            log.warning("analyze %s: %s", slug, exc)
            yield _sse({"type": "error", "message": f"AI analysis failed: {exc}"})
            return
        yield _sse({"type": "result", "analysis": analysis})
        yield _sse({"type": "done"})

    return _sse_response(event_stream())
