"""Admin: list problems, view/edit a problem's source, add one, or AI-generate.

No real auth (this is a home/LAN instance). If you expose lootcode beyond a
trusted network, put this router behind authentication.
"""
from __future__ import annotations

import json
import math
import queue
import threading
from types import SimpleNamespace
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import content, store
from ..config import settings
from ..db import get_db
from ..executor import run_submission
from ..llm import draft_store
from ..models import Problem
from ..problem_validation import (
    existing_slugs,
    find_similar_problems,
    suggest_slug,
    validate_problem,
)
from ..templating import templates
from .pages import _page_window

router = APIRouter(prefix="/admin")

COMPARE_MODES = ("exact", "unordered", "set_of_lists")

# Human-readable label for the LLM backend the generator will use, for the UI.
_BACKEND_LABELS = {
    "anthropic": "Claude API",
    "openai": "local LLM endpoint (LLM_HELP_URL)",
}


def _active_backend() -> str:
    """Which generation backend is live ('anthropic' | 'openai' | ''). Imported
    lazily so admin listing doesn't pull in the generator's LLM deps."""
    from ..llm.generator import active_backend

    return active_backend()

# The admin table is happy to show far more per page than the public list; only
# once the bank grows past this do we paginate.
ADMIN_PROBLEMS_PER_PAGE = 1000


def _save(db: Session, data: dict) -> Problem:
    """Persist a problem to the DB and mirror it into content/ on disk."""
    prob = store.upsert_problem(db, data)
    try:
        content.write_problem_files(data)
    except OSError:
        pass  # DB is the source of truth at runtime; file mirror is best-effort
    return prob


def _parse_params(text: str) -> list[dict]:
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        name, _, typ = line.partition(":")
        out.append({"name": name.strip(), "type": typ.strip() or "any"})
    return out


def _form_to_data(*, slug, title, difficulty, topics, hints, statement_md,
                  function_name, params, return_type, compare, starter_code,
                  canonical_solution, tests_json, source) -> dict:
    tests = json.loads(tests_json)
    if not isinstance(tests, list) or not tests:
        raise ValueError("Tests must be a non-empty JSON array.")
    return {
        "slug": slug.strip(), "title": title.strip(), "difficulty": difficulty,
        "topics": [t.strip() for t in topics.split(",") if t.strip()],
        # One hint per line; normalize_hints trims blanks and caps at MAX_HINTS.
        "hints": content.normalize_hints(hints.splitlines()),
        "statement_md": statement_md, "function_name": function_name.strip(),
        "params": _parse_params(params), "return_type": return_type.strip(),
        "compare": compare if compare in COMPARE_MODES else "exact",
        "starter_code": starter_code, "canonical_solution": canonical_solution or None,
        "scoring_type": "weighted", "points": 100, "source": source,
        "time_limit_ms": settings.EXEC_TIME_LIMIT_MS,
        "memory_limit_mb": settings.EXEC_MEMORY_LIMIT_MB, "tests": tests,
    }


def _form_view(prob: Problem) -> dict:
    """Serialize a Problem into the strings the edit form expects."""
    return {
        "slug": prob.slug, "title": prob.title, "difficulty": prob.difficulty,
        "topics": ", ".join(prob.topics or []),
        "hints": "\n".join(prob.hints or []),
        "statement_md": prob.statement_md or "",
        "function_name": prob.function_name,
        "params": "\n".join(f"{p['name']}: {p.get('type', 'any')}" for p in prob.params),
        "return_type": prob.return_type or "", "compare": prob.compare or "exact",
        "starter_code": prob.starter_code or "",
        "canonical_solution": prob.canonical_solution or "",
        "tests_json": json.dumps(
            [{"name": t.name, "input": t.input, "expected": t.expected,
              "weight": t.weight, "hidden": t.hidden} for t in prob.tests], indent=2),
    }


# The starter example shown in an empty "New problem" form (bound as the tests
# field's initial value so the author sees the exact shape a test case takes).
_EXAMPLE_TESTS_JSON = """[
  {"name": "example-1", "input": {"s": "hello"}, "expected": "olleh", "weight": 1, "hidden": false},
  {"name": "hidden-1", "input": {"s": ""}, "expected": "", "weight": 1, "hidden": true}
]"""


def _blank_form() -> dict:
    """Empty field values for a fresh New-problem form."""
    return {"slug": "", "title": "", "difficulty": "easy", "topics": "", "hints": "",
            "statement_md": "", "function_name": "", "params": "", "return_type": "",
            "compare": "exact", "starter_code": "", "canonical_solution": "",
            "tests_json": _EXAMPLE_TESTS_JSON}


def _data_to_form(data: dict) -> dict:
    """Serialize an internal problem dict into the strings the New/review form binds
    (mirror of :func:`_form_view` but from a plain dict, e.g. an AI-generated draft)."""
    params = [p for p in (data.get("params") or [])
              if isinstance(p, dict) and p.get("name")]
    return {
        "slug": data.get("slug", "") or "", "title": data.get("title", "") or "",
        "difficulty": data.get("difficulty", "easy") or "easy",
        "topics": ", ".join(data.get("topics") or []),
        "hints": "\n".join(data.get("hints") or []),
        "statement_md": data.get("statement_md", "") or "",
        "function_name": data.get("function_name", "") or "",
        "params": "\n".join(f"{p['name']}: {p.get('type', 'any')}" for p in params),
        "return_type": data.get("return_type", "") or "",
        "compare": data.get("compare", "exact") or "exact",
        "starter_code": data.get("starter_code", "") or "",
        "canonical_solution": data.get("canonical_solution", "") or "",
        "tests_json": json.dumps(
            [{"name": t.get("name"), "input": t.get("input"),
              "expected": t.get("expected"), "weight": t.get("weight", 1),
              "hidden": t.get("hidden", False)} for t in (data.get("tests") or [])],
            indent=2),
    }


def _raw_form(**fields: str) -> dict:
    """Echo exactly what the user submitted back into the form (so a validation
    failure never loses their edits, including verbatim test JSON)."""
    return {k: (v if v is not None else "") for k, v in fields.items()}


def _new_context(request: Request, *, f: dict, errors=None, warnings=None,
                 ai: bool = False, draft_id: str = "", source: str = "manual",
                 collision: bool = False, original_slug: str = "",
                 suggested_slug: str = "", similar=None, generation=None,
                 pending_count: int = 0) -> dict:
    """Template context for admin/new.html (shared by manual create and AI review)."""
    return {
        "request": request, "user_name": request.state.user_name,
        "compare_modes": COMPARE_MODES, "f": f,
        "errors": errors or [], "warnings": warnings or [],
        "ai": ai, "draft_id": draft_id, "source": source,
        "collision": collision, "original_slug": original_slug,
        "suggested_slug": suggested_slug, "similar": similar or [],
        "generation": generation or {}, "pending_count": pending_count,
    }


# --- list -----------------------------------------------------------------
@router.get("")
def dashboard(request: Request, q: str | None = None, page: int = 1,
              db: Session = Depends(get_db)):
    stmt = select(Problem)
    if q:
        # Admin search is a bit wider than the public list: match slug or title,
        # since the admin identifies problems by slug.
        like = f"%{q}%"
        stmt = stmt.where(or_(Problem.slug.ilike(like), Problem.title.ilike(like)))
    problems = list(db.scalars(stmt.order_by(Problem.id)))

    # Paginate. `page` is clamped so a stale/oversized link lands on the last page
    # rather than an empty one.
    total = len(problems)
    pages = max(1, math.ceil(total / ADMIN_PROBLEMS_PER_PAGE))
    page = max(1, min(page, pages))
    start = (page - 1) * ADMIN_PROBLEMS_PER_PAGE
    page_problems = problems[start:start + ADMIN_PROBLEMS_PER_PAGE]

    base_qs = urlencode({k: v for k, v in (("q", q),) if v})

    return templates.TemplateResponse(request, "admin/index.html", {
        "request": request, "problems": page_problems,
        "user_name": request.state.user_name,
        "f_q": q or "", "total": total,
        "page": page, "pages": pages, "base_qs": base_qs,
        "page_items": _page_window(page, pages),
        "range_start": start + 1 if total else 0,
        "range_end": start + len(page_problems),
        "gen_enabled": settings.generation_enabled,
        "gen_backend": _BACKEND_LABELS.get(_active_backend(), ""),
    })


# --- view / edit a problem's source ---------------------------------------
@router.get("/problems/{slug}/edit")
def edit_form(slug: str, request: Request, db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return templates.TemplateResponse(request, "admin/edit.html", {
        "request": request, "user_name": request.state.user_name,
        "f": _form_view(prob), "compare_modes": COMPARE_MODES,
        "errors": [], "warnings": [], "saved": False,
    })


@router.post("/problems/{slug}/edit")
def edit_submit(
    slug: str, request: Request, db: Session = Depends(get_db),
    title: str = Form(""), difficulty: str = Form("easy"), topics: str = Form(""),
    hints: str = Form(""),
    statement_md: str = Form(""), function_name: str = Form(""), params: str = Form(""),
    return_type: str = Form(""), compare: str = Form("exact"),
    starter_code: str = Form(""), canonical_solution: str = Form(""),
    tests_json: str = Form("[]"),
):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    # The slug is the identity and isn't editable here, so the values the author
    # typed live in these locals; echo them straight back on any failure.
    typed = {"slug": slug, "title": title, "difficulty": difficulty, "topics": topics,
             "hints": hints, "statement_md": statement_md,
             "function_name": function_name, "params": params,
             "return_type": return_type, "compare": compare,
             "starter_code": starter_code, "canonical_solution": canonical_solution,
             "tests_json": tests_json}

    def _reject(errors, warnings=None):
        return templates.TemplateResponse(request, "admin/edit.html", {
            "request": request, "user_name": request.state.user_name,
            "f": typed, "compare_modes": COMPARE_MODES,
            "errors": errors, "warnings": warnings or [], "saved": False,
        }, status_code=400)

    try:
        data = _form_to_data(
            slug=slug, title=title, difficulty=difficulty, topics=topics, hints=hints,
            statement_md=statement_md, function_name=function_name, params=params,
            return_type=return_type, compare=compare, starter_code=starter_code,
            canonical_solution=canonical_solution, tests_json=tests_json,
            source=prob.source,  # preserve original source
        )
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return _reject([f"Tests must be a valid JSON array of test objects: {exc}"])

    # Same gate as create, minus the slug-collision check (editing in place).
    result = validate_problem(data, db=db, is_new=False)
    if not result.ok:
        return _reject(result.errors, result.warnings)

    _save(db, data)
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    return templates.TemplateResponse(request, "admin/edit.html", {
        "request": request, "user_name": request.state.user_name,
        "f": _form_view(prob), "compare_modes": COMPARE_MODES,
        "errors": [], "warnings": result.warnings, "saved": True,
    })


# --- run a solution against the current (unsaved) tests --------------------
class VerifyBody(BaseModel):
    code: str
    function_name: str
    params: str = ""
    return_type: str = ""
    tests_json: str = "[]"
    compare: str = "exact"


@router.post("/problems/{slug}/verify")
def verify(slug: str, body: VerifyBody):
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="The solution is empty.")
    try:
        tests_raw = json.loads(body.tests_json)
        if not isinstance(tests_raw, list) or not tests_raw:
            raise ValueError("Tests must be a non-empty JSON array.")
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid tests JSON: {exc}")

    prob = SimpleNamespace(
        function_name=body.function_name.strip(), params=_parse_params(body.params),
        return_type=body.return_type.strip(),
        time_limit_ms=settings.EXEC_TIME_LIMIT_MS,
        memory_limit_mb=settings.EXEC_MEMORY_LIMIT_MB, points=100,
        compare=body.compare if body.compare in COMPARE_MODES else "exact",
    )
    tests = [SimpleNamespace(
        name=t.get("name", f"test-{i + 1}"), input=t.get("input", {}),
        expected=t.get("expected"), weight=t.get("weight", 1),
        hidden=t.get("hidden", False)) for i, t in enumerate(tests_raw)]

    g = run_submission(body.code, prob, tests)
    # Admin sees full detail (including hidden tests' expected/actual).
    return {
        "solved": g.solved, "score": g.score, "passed_count": g.passed_count,
        "total_count": g.total_count, "runtime_ms": round(g.runtime_ms, 1),
        "results": [{
            "name": r.name, "hidden": r.hidden, "passed": r.passed, "status": r.status,
            "time_ms": round(r.time_ms or 0, 1), "expected": tests[i].expected,
            "actual": r.returned, "error": r.error,
        } for i, r in enumerate(g.results)],
    }


# --- create new -----------------------------------------------------------
@router.get("/new")
def new_form(request: Request):
    return templates.TemplateResponse(
        request, "admin/new.html", _new_context(request, f=_blank_form()))


@router.post("/new")
def new_submit(
    request: Request, db: Session = Depends(get_db),
    slug: str = Form(""), title: str = Form(""), difficulty: str = Form("easy"),
    topics: str = Form(""), hints: str = Form(""), statement_md: str = Form(""),
    function_name: str = Form(""), params: str = Form(""), return_type: str = Form(""),
    compare: str = Form("exact"), starter_code: str = Form(""),
    canonical_solution: str = Form(""), tests_json: str = Form("[]"),
    source: str = Form("manual"), draft_id: str = Form(""),
):
    """Create a problem — the single validated save path for BOTH the manual form
    and the AI review page (which posts here with source='ai' + its draft_id).

    Every field is validated before anything is written (validate_problem): slug
    format + collision, structure, canonical tags, statement/judge consistency, and
    the canonical passing all its tests in the sandbox. On any error the form is
    re-rendered with the messages and the author's exact input preserved — nothing
    reaches the DB or content/ until it is a coherent, verified problem.
    """
    source = source if source in ("manual", "ai") else "manual"
    is_ai = source == "ai"
    raw = _raw_form(
        slug=slug, title=title, difficulty=difficulty, topics=topics, hints=hints,
        statement_md=statement_md, function_name=function_name, params=params,
        return_type=return_type, compare=compare, starter_code=starter_code,
        canonical_solution=canonical_solution, tests_json=tests_json)

    def _reject(errors, warnings=None):
        # Recompute the AI-review extras so a failed Create still shows the banner,
        # collision hint, and similar-problem list.
        similar, collision, orig, suggested, gen, pending = [], False, "", "", {}, 0
        if is_ai:
            ex = existing_slugs(db)
            collision = bool(slug) and slug in ex
            orig, suggested = slug, (suggest_slug(slug, ex) if collision else "")
            similar = find_similar_problems(
                db, slug=slug, title=title,
                tags=[t.strip() for t in topics.split(",") if t.strip()])
            draft = draft_store.get(draft_id) if draft_id else None
            gen = (draft or {}).get("_validation", {})
            pending = len(draft_store.items())
        return templates.TemplateResponse(request, "admin/new.html", _new_context(
            request, f=raw, errors=errors, warnings=warnings, ai=is_ai,
            draft_id=draft_id, source=source, collision=collision,
            original_slug=orig, suggested_slug=suggested, similar=similar,
            generation=gen, pending_count=pending), status_code=400)

    # Build the internal dict (bad test JSON fails here, before validation).
    try:
        data = _form_to_data(
            slug=slug, title=title, difficulty=difficulty, topics=topics, hints=hints,
            statement_md=statement_md, function_name=function_name, params=params,
            return_type=return_type, compare=compare, starter_code=starter_code,
            canonical_solution=canonical_solution, tests_json=tests_json, source=source)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return _reject([f"Tests must be a valid JSON array of test objects: {exc}"])

    result = validate_problem(data, db=db, is_new=True)
    if not result.ok:
        return _reject(result.errors, result.warnings)

    prob = _save(db, data)
    if draft_id:
        draft_store.pop(draft_id)  # confirmed → drop the pending draft
    return RedirectResponse(f"/admin/problems/{prob.slug}/edit", status_code=303)


# --- AI generation --------------------------------------------------------
# Generation NEVER writes to the bank directly. It produces one or more *drafts*
# (held in app.llm.draft_store) and sends the author to a review page that is the
# manual New-problem form, prefilled — so they confirm/edit every field and Create
# through the same validated save path (POST /admin/new). This is what makes AI
# authoring safe: a slug collision can't silently overwrite a problem, and a
# canonical that doesn't verify can't land, because a human clears the same gate.
@router.get("/generate")
def generate_form(request: Request):
    return templates.TemplateResponse(request, "admin/generate.html", {
        "request": request, "user_name": request.state.user_name,
        "disabled": not settings.generation_enabled, "error": None,
        "backend": _BACKEND_LABELS.get(_active_backend(), ""),
    })


def _generate(*, brief: str, difficulty: str, bulk_text: str, count: int,
              on_progress, sink) -> None:
    """Generate problems WITHOUT saving; call ``sink(draft_id, data)`` per finished
    problem (each stashed as a review draft). Raises ValueError when neither a brief
    nor bulk material was supplied."""
    from ..llm import generator

    def stash(data: dict) -> None:
        sink(draft_store.add(data), data)

    if bulk_text:
        generator.generate_from_text(bulk_text, count, on_progress=on_progress,
                                     on_problem=stash)
    elif brief:
        data = generator.generate_problem(brief, difficulty or None,
                                          on_progress=on_progress)
        stash(data)
    else:
        raise ValueError("Enter a problem idea or paste source material.")


def _review_redirect(draft_ids: list[str]) -> str:
    """Straight to the single draft's review page, or the queue for a batch."""
    if len(draft_ids) == 1:
        return f"/admin/generate/review/{draft_ids[0]}"
    return "/admin/generate/review"


@router.post("/generate")
def generate_submit(
    request: Request,
    brief: str = Form(""), difficulty: str = Form(""),
    bulk_text: str = Form(""), count: int = Form(3),
):
    """No-JS fallback: generate (blocking), then redirect to the review page(s)."""
    if not settings.generation_enabled:
        raise HTTPException(status_code=400, detail="AI generation is not configured.")

    ids: list[str] = []
    try:
        _generate(brief=brief.strip(), difficulty=difficulty.strip(),
                  bulk_text=bulk_text.strip(), count=count, on_progress=None,
                  sink=lambda did, data: ids.append(did))
    except Exception as exc:  # noqa: BLE001 - surface any generation/parse error
        return templates.TemplateResponse(request, "admin/generate.html", {
            "request": request, "user_name": request.state.user_name,
            "disabled": False, "error": f"Generation failed: {exc}",
            "backend": _BACKEND_LABELS.get(_active_backend(), ""),
        }, status_code=400)
    if not ids:
        return templates.TemplateResponse(request, "admin/generate.html", {
            "request": request, "user_name": request.state.user_name,
            "disabled": False, "error": "No problems were generated — try again.",
            "backend": _BACKEND_LABELS.get(_active_backend(), ""),
        }, status_code=400)
    return RedirectResponse(_review_redirect(ids), status_code=303)


@router.post("/generate/stream")
def generate_stream(
    brief: str = Form(""), difficulty: str = Form(""),
    bulk_text: str = Form(""), count: int = Form(3),
):
    """Server-Sent Events variant of ``POST /generate``.

    Generation on a local endpoint takes the better part of a minute, so instead of a
    blank blocking POST we run it in a worker thread and stream coarse progress. Each
    finished problem becomes a review draft; when the run ends we emit
    ``{"type": "done", "redirect": <review-url>}`` and the browser navigates there —
    nothing is saved yet. Mirrors the streaming shape of the "Get More Help with AI"
    endpoint (see app/routers/submissions.py).
    """
    if not settings.generation_enabled:
        raise HTTPException(status_code=400, detail="AI generation is not configured.")
    brief, difficulty, bulk_text = brief.strip(), difficulty.strip(), bulk_text.strip()

    events: queue.Queue = queue.Queue()

    def worker():
        ids: list[str] = []
        try:
            def on_progress(msg: str):
                events.put({"type": "status", "message": msg})

            def sink(did: str, data: dict):
                ids.append(did)
                events.put({"type": "status", "message":
                            f"Drafted “{data.get('title') or data.get('slug')}” — "
                            "ready for review."})

            _generate(brief=brief, difficulty=difficulty, bulk_text=bulk_text,
                      count=count, on_progress=on_progress, sink=sink)
            if not ids:
                events.put({"type": "error",
                            "message": "No problems were generated — try again."})
            else:
                events.put({"type": "done", "redirect": _review_redirect(ids)})
        except Exception as exc:  # noqa: BLE001 - surface any generation/parse error
            events.put({"type": "error", "message": f"Generation failed: {exc}"})
        finally:
            events.put(None)  # sentinel: end of stream

    threading.Thread(target=worker, daemon=True).start()

    def event_stream():
        while True:
            item = events.get()
            if item is None:
                break
            yield f"data: {json.dumps(item)}\n\n"

    return StreamingResponse(
        event_stream(), media_type="text/event-stream",
        # Defeat proxy/browser buffering so frames arrive as they're produced.
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


# --- review AI-generated drafts before saving -----------------------------
@router.get("/generate/review")
def generate_review_list(request: Request, db: Session = Depends(get_db)):
    """The pending-draft queue (where a batch generation lands)."""
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


@router.get("/generate/review/{draft_id}")
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

    f = _data_to_form(data)
    if collision and suggested:
        # Pre-fill a free slug so a naive Create can't overwrite; the banner explains.
        f = {**f, "slug": suggested}

    return templates.TemplateResponse(request, "admin/new.html", _new_context(
        request, f=f, ai=True, draft_id=draft_id, source="ai",
        collision=collision, original_slug=slug, suggested_slug=suggested,
        similar=similar, generation=data.get("_validation", {}),
        pending_count=len(draft_store.items())))
