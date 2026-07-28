"""Admin: AI problem generation (two-step: idea → statement → full problem).

Generation NEVER writes to the bank directly, and it is ONE problem at a time.
The owner either (choice 1) turns an idea into a problem *statement*, or
(choice 2) provides a statement directly; then — after a duplicate check keyed
off the statement's inferred title/slug — the statement is filled in to a full
problem (contract + canonical + tests + hints), exactly the CLI Mode-A pipeline
(scripts/generate_problem_from_statement.py). The finished problem is stashed as
a *draft* and the owner is sent to the review page (the New-problem form,
prefilled) to confirm/edit every field and Create through the same validated
save path (POST /admin/new, in `admin_problems.py`). That is what keeps AI
authoring safe: a slug collision can't silently overwrite a problem, and a
canonical that doesn't verify can't land, because a human clears the same gate.
"""
from __future__ import annotations

import json
import queue
import threading

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..llm import draft_store
from ..problem_validation import existing_slugs, find_similar_problems, suggest_slug
from ..templating import templates
from .admin_forms import new_context, to_form

router = APIRouter(prefix="/generate")


def _backend_label() -> str:
    """Imported lazily so rendering a page doesn't pull in the generator's LLM deps."""
    from ..llm.generator import backend_label

    return backend_label()


def _generate_page(request: Request, *, error: str | None = None,
                   status_code: int = 200):
    """Render the two-choice generation landing page (optionally with an error)."""
    return templates.TemplateResponse(request, "admin/generate.html", {
        "request": request, "user_name": request.state.user_name,
        "disabled": not settings.generation_enabled, "error": error,
        "backend": _backend_label(),
    }, status_code=status_code)


def _require_enabled() -> None:
    if not settings.generation_enabled:
        raise HTTPException(status_code=400, detail="AI generation is not configured.")


def _sse_stream(work) -> StreamingResponse:  # noqa: ANN001
    """Run ``work(put)`` in a worker thread and stream whatever it ``put(...)``s as
    Server-Sent Events. The worker reports coarse ``{"type":"status"}`` frames and
    ends with a ``{"type":"done","redirect": url}`` (the browser navigates there);
    any exception becomes a final ``{"type":"error"}``. Mirrors the SSE shape of the
    "Get More Help with AI" endpoint so the client JS is the same pattern.
    """
    events: queue.Queue = queue.Queue()

    def runner():
        try:
            work(lambda ev: events.put(ev))
        except Exception as exc:  # noqa: BLE001 - surface any generation/parse error
            events.put({"type": "error", "message": str(exc)})
        finally:
            events.put(None)  # sentinel: end of stream

    threading.Thread(target=runner, daemon=True).start()

    def event_stream():
        while True:
            item = events.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_stream(), media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("")
def generate_form(request: Request):
    """Landing page: choose to start from an idea (→ statement) or a statement."""
    return _generate_page(request)


# --- choice 1: idea → problem statement -----------------------------------
@router.post("/statement/stream")
def statement_stream(idea: str = Form(""), difficulty: str = Form("")):
    """SSE: write a problem statement from an idea, then redirect to the statement
    page (choice 1, step 1). Only the *statement* is produced here — the full
    problem is generated from it on the next page."""
    _require_enabled()
    idea, difficulty = idea.strip(), difficulty.strip()

    def work(put):
        from ..llm import generator, statement_store
        statement = generator.generate_statement(
            idea, difficulty or None,
            on_progress=lambda m: put({"type": "status", "message": m}))
        sid = statement_store.add(statement)
        put({"type": "done", "redirect": f"/admin/generate/statement/{sid}"})

    return _sse_stream(work)


@router.post("/statement")
def statement_submit(request: Request, idea: str = Form(""),
                     difficulty: str = Form("")):
    """No-JS fallback for choice 1: write the statement (blocking), then redirect."""
    _require_enabled()
    from ..llm import generator, statement_store
    try:
        statement = generator.generate_statement(idea.strip(), difficulty.strip() or None)
    except Exception as exc:  # noqa: BLE001 - surface any generation error
        return _generate_page(request, error=f"Could not write a statement: {exc}",
                              status_code=400)
    sid = statement_store.add(statement)
    return RedirectResponse(f"/admin/generate/statement/{sid}", status_code=303)


# --- choice 2 entry: an owner-provided statement --------------------------
@router.post("/from-statement")
def from_statement_submit(request: Request, statement: str = Form("")):
    """Choice 2: take a pasted statement straight to the statement page (where the
    duplicate check runs and the full problem is generated)."""
    _require_enabled()
    from ..llm import statement_store
    statement = statement.strip()
    if not statement:
        return _generate_page(request, error="Paste a problem statement to continue.",
                              status_code=400)
    sid = statement_store.add(statement)
    return RedirectResponse(f"/admin/generate/statement/{sid}", status_code=303)


# --- the statement page: duplicate check, then generate the full problem ---
def _duplicate_check(db: Session, statement: str) -> dict:
    """Infer a title + slug for a statement (one cheap LLM call) and use them to
    surface the top similar existing problems — the "is this already in the bank?"
    nudge that sits between writing a statement and filling it in."""
    from ..llm import generator
    try:
        named = generator.suggest_title_slug(statement)
    except Exception:  # noqa: BLE001 - naming is best-effort; degrade to no suggestion
        named = {"title": "", "slug": ""}
    similar = find_similar_problems(
        db, slug=named.get("slug", ""), title=named.get("title", ""), tags=None)
    return {"title": named.get("title", ""), "slug": named.get("slug", ""),
            "similar": similar}


def _statement_context(request: Request, db: Session, sid: str, entry: dict,
                       *, error: str | None = None) -> dict:
    check = entry.get("check")
    if check is None:
        check = _duplicate_check(db, entry["statement"])
        from ..llm import statement_store
        statement_store.set_check(sid, check)
    return {
        "request": request, "user_name": request.state.user_name,
        "sid": sid, "statement": entry["statement"],
        "title": check["title"], "slug": check["slug"], "similar": check["similar"],
        "backend": _backend_label(),
        "disabled": not settings.generation_enabled, "error": error,
    }


@router.get("/statement/{sid}")
def statement_review(sid: str, request: Request, db: Session = Depends(get_db)):
    """Show the (editable) statement with a duplicate check, and a button to
    generate the full problem from it."""
    from ..llm import statement_store
    entry = statement_store.get(sid)
    if entry is None:  # expired / already consumed — back to the start
        return RedirectResponse("/admin/generate", status_code=303)
    return templates.TemplateResponse(
        request, "admin/generate_statement.html",
        _statement_context(request, db, sid, entry))


@router.post("/duplicate-check")
def duplicate_check_api(sid: str = Form(""), statement: str = Form(""),
                        db: Session = Depends(get_db)):
    """JSON: re-run the duplicate check for the current (possibly edited) statement.
    Called by the statement page so the similar-problem list reflects live edits."""
    statement = statement.strip()
    if not statement:
        return {"title": "", "slug": "", "similar": []}
    from ..llm import statement_store
    if sid:
        statement_store.set_statement(sid, statement)
    check = _duplicate_check(db, statement)
    if sid:
        statement_store.set_check(sid, check)
    return check


@router.post("/full/stream")
def full_stream(sid: str = Form(""), statement: str = Form(""),
                title: str = Form(""), slug: str = Form("")):
    """SSE: generate the full problem from the statement, stash it as a review
    draft, then redirect to its review page."""
    _require_enabled()
    statement, title, slug = statement.strip(), title.strip(), slug.strip()

    def work(put):
        from ..llm import generator, statement_store
        data = generator.generate_from_statement(
            statement, title=title, slug=slug,
            on_progress=lambda m: put({"type": "status", "message": m}))
        did = draft_store.add(data)
        if sid:
            statement_store.pop(sid)
        put({"type": "status", "message":
             f"Drafted “{data.get('title') or data.get('slug')}” — ready for review."})
        put({"type": "done", "redirect": f"/admin/generate/review/{did}"})

    return _sse_stream(work)


@router.post("/full")
def full_submit(request: Request, sid: str = Form(""), statement: str = Form(""),
                title: str = Form(""), slug: str = Form(""),
                db: Session = Depends(get_db)):
    """No-JS fallback: generate the full problem (blocking), then redirect to review."""
    _require_enabled()
    from ..llm import generator, statement_store
    statement = statement.strip()
    if not statement:
        entry = statement_store.get(sid)
        if entry is not None:
            return templates.TemplateResponse(
                request, "admin/generate_statement.html",
                _statement_context(request, db, sid, entry,
                                   error="A problem statement is required."),
                status_code=400)
        return _generate_page(request, error="A problem statement is required.",
                              status_code=400)
    try:
        data = generator.generate_from_statement(
            statement, title=title.strip(), slug=slug.strip())
    except Exception as exc:  # noqa: BLE001 - surface any generation/parse error
        entry = statement_store.get(sid)
        if entry is not None:
            statement_store.set_statement(sid, statement)
            entry = statement_store.get(sid) or entry
            return templates.TemplateResponse(
                request, "admin/generate_statement.html",
                _statement_context(request, db, sid, entry,
                                   error=f"Generation failed: {exc}"),
                status_code=400)
        return _generate_page(request, error=f"Generation failed: {exc}",
                              status_code=400)
    did = draft_store.add(data)
    if sid:
        statement_store.pop(sid)
    return RedirectResponse(f"/admin/generate/review/{did}", status_code=303)


# --- review AI-generated drafts before saving -----------------------------
@router.get("/review")
def generate_review_list(request: Request, db: Session = Depends(get_db)):
    """The pending-draft queue. One problem is generated at a time, but a draft
    persists until Created or evicted, so more than one can be waiting here."""
    ex = existing_slugs(db)
    drafts = []
    for did, data in draft_store.items():
        slug = data.get("slug", "")
        v = data.get("_validation", {})
        drafts.append({
            "id": did, "slug": slug, "title": data.get("title") or slug,
            "difficulty": data.get("difficulty", ""),
            "n_tests": len(data.get("tests") or []),
            "collision": bool(slug) and slug in ex,
            "verified": bool(v.get("solved")),
            "passed": v.get("passed"), "total": v.get("total"),
        })
    return templates.TemplateResponse(request, "admin/generate_review_list.html", {
        "request": request, "user_name": request.state.user_name, "drafts": drafts,
    })


@router.get("/review/{draft_id}")
def generate_review(draft_id: str, request: Request, db: Session = Depends(get_db)):
    """Render an AI draft in the New-problem form, prefilled, with a duplicate/
    collision check and similar-problem suggestions. Saving posts to /admin/new."""
    data = draft_store.get(draft_id)
    if data is None:  # expired, or already saved — fall back to the queue
        return RedirectResponse("/admin/generate/review", status_code=303)

    ex = existing_slugs(db)
    slug = data.get("slug", "")
    collision = bool(slug) and slug in ex
    suggested = suggest_slug(slug, ex) if collision else ""
    similar = find_similar_problems(
        db, slug=slug, title=data.get("title", ""), tags=data.get("topics"))

    f = to_form(data)
    if collision and suggested:
        # Pre-fill a free slug so a naive Create can't overwrite; the banner explains.
        f = {**f, "slug": suggested}

    return templates.TemplateResponse(request, "admin/new.html", new_context(
        request, f=f, ai=True, draft_id=draft_id, source="ai",
        collision=collision, original_slug=slug, suggested_slug=suggested,
        similar=similar, generation=data.get("_validation", {}),
        pending_count=len(draft_store.items())))
