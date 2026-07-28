"""Admin CRUD: list problems, edit one, verify a solution, create a new one.

No real auth (this is a home/LAN instance) — see `docs/security.md` for the
trust boundary. If you expose lootcode beyond a trusted network, put this
router behind authentication.
"""
from __future__ import annotations

import json
import math
from types import SimpleNamespace
from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import content, store
from ..config import settings
from ..db import get_db
from ..executor import run_submission
from ..llm import draft_store
from ..logging_config import audit, get_logger
from ..models import Problem
from ..pagination import page_window
from ..problem_validation import (
    existing_slugs,
    find_similar_problems,
    suggest_slug,
    validate_problem,
)
from ..templating import templates
from .admin_forms import (
    COMPARE_MODES,
    KINDS,
    NewProblemForm,
    ProblemForm,
    blank_form,
    new_context,
    parse_params,
    to_data,
    to_form,
)

log = get_logger(__name__)

router = APIRouter()

# The admin table is happy to show far more per page than the public list; only
# once the bank grows past this do we paginate.
ADMIN_PROBLEMS_PER_PAGE = 1000


def _save(db: Session, data: dict) -> tuple[Problem, str]:
    """Persist a problem to the DB and mirror it into content/ on disk.

    Returns the saved problem and a **mirror-failure message** — empty when the
    disk write succeeded. The DB write has already committed by the time a mirror
    can fail, so this is not a rollback: it is reporting a partial save honestly
    instead of reporting success. This used to be ``except OSError: pass``, which
    let a full disk or a read-only mount desync the DB from the durable source of
    truth with no log line and nothing shown to the author.
    """
    prob = store.upsert_problem(db, data)
    slug = data["slug"]
    root = content.owning_root(slug)
    try:
        content.write_problem_files(data, root)
    except OSError as exc:
        log.exception("failed to mirror %r into %s — the database and content/ "
                      "are now out of step for this problem", slug, root)
        audit("saved problem %r to the DB but FAILED to write it to %s", slug, root)
        return prob, (
            f"Saved to the database, but writing {slug} to {root} failed: {exc}. "
            "content/ is now out of step — fix the disk problem and save again "
            "before the next re-seed, or the change will be lost.")
    audit("saved problem %r to %s (%d tests)", slug, root,
          len(data.get("tests") or []))
    return prob, ""


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

    # Imported lazily so listing problems doesn't pull in the generator's LLM deps.
    from ..llm.generator import backend_label

    return templates.TemplateResponse(request, "admin/index.html", {
        "request": request, "problems": page_problems,
        "user_name": request.state.user_name,
        "f_q": q or "", "total": total,
        "page": page, "pages": pages, "base_qs": base_qs,
        "page_items": page_window(page, pages),
        "range_start": start + 1 if total else 0,
        "range_end": start + len(page_problems),
        "gen_enabled": settings.generation_enabled,
        "gen_backend": backend_label(),
    })


# --- view / edit a problem's source ---------------------------------------
def _edit_page(request: Request, f: dict, *, errors=None, warnings=None,  # noqa: ANN001
               saved: bool = False, status_code: int = 200):
    return templates.TemplateResponse(request, "admin/edit.html", {
        "request": request, "user_name": request.state.user_name,
        "f": f, "compare_modes": COMPARE_MODES,
        "errors": errors or [], "warnings": warnings or [], "saved": saved,
    }, status_code=status_code)


@router.get("/problems/{slug}/edit")
def edit_form(slug: str, request: Request, db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return _edit_page(request, to_form(prob))


@router.post("/problems/{slug}/edit")
def edit_submit(slug: str, request: Request,
                form: Annotated[ProblemForm, Form()],
                db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")

    # The slug is the identity and isn't editable here, so it comes from the path;
    # everything else is echoed straight back on any failure so a rejected save
    # never costs the author their edits.
    typed = form.echo(slug=slug)

    try:
        data = to_data(form, slug=slug, source=prob.source)  # preserve original source
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return _edit_page(request, typed, status_code=400, errors=[
            f"Tests must be a valid JSON array of test objects: {exc}"])

    # Same gate as create, minus the slug-collision check (editing in place).
    result = validate_problem(data, db=db, is_new=False)
    if not result.ok:
        return _edit_page(request, typed, errors=result.errors,
                          warnings=result.warnings, status_code=400)

    prob, mirror_error = _save(db, data)
    # A mirror failure is not a validation error — the save happened — but the
    # author has to know their edit only reached the DB.
    return _edit_page(request, to_form(prob), saved=True,
                      warnings=[*result.warnings,
                                *([mirror_error] if mirror_error else [])])


# --- run a solution against the current (unsaved) tests --------------------
class VerifyBody(BaseModel):
    code: str
    kind: str = "function"
    function_name: str = ""
    params: str = ""
    return_type: str = ""
    class_name: str = ""
    class_methods_json: str = "[]"
    tests_json: str = "[]"
    compare: str = "exact"


def _run_verify(body: VerifyBody) -> dict:
    """Run a solution against the posted (unsaved) tests and return full admin
    detail. Shared by the edit page and the AI review page — neither needs a saved
    problem; everything comes from the form fields in ``body``."""
    if not body.code.strip():
        raise HTTPException(status_code=400, detail="The solution is empty.")
    try:
        tests_raw = json.loads(body.tests_json)
        if not isinstance(tests_raw, list) or not tests_raw:
            raise ValueError("Tests must be a non-empty JSON array.")
    except (ValueError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=400, detail=f"Invalid tests JSON: {exc}") from exc

    kind = body.kind if body.kind in KINDS else "function"
    class_methods = None
    if kind == "class":
        try:
            class_methods = json.loads(body.class_methods_json or "[]")
            if not isinstance(class_methods, list):
                raise ValueError("Class methods must be a JSON array.")
        except (ValueError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid class methods JSON: {exc}") from exc

    prob = {
        "kind": kind,
        "function_name": body.function_name.strip(),
        "params": parse_params(body.params),
        "return_type": body.return_type.strip(),
        "class_name": body.class_name.strip() or None,
        "class_methods": class_methods,
        "time_limit_ms": settings.EXEC_TIME_LIMIT_MS,
        "memory_limit_mb": settings.EXEC_MEMORY_LIMIT_MB, "points": 100,
        "compare": body.compare if body.compare in COMPARE_MODES else "exact",
    }
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


@router.post("/problems/{slug}/verify")
def verify(slug: str, body: VerifyBody):
    """Edit page: run the canonical against the current tests (slug is unused —
    the run is entirely from ``body`` — but keeps the per-problem URL)."""
    return _run_verify(body)


@router.post("/verify")
def verify_unsaved(body: VerifyBody):
    """AI review page (and the New-problem form): same run for a draft that has no
    slug yet, so authors get feedback before Create."""
    return _run_verify(body)


# --- create new -----------------------------------------------------------
@router.get("/new")
def new_form(request: Request):
    return templates.TemplateResponse(
        request, "admin/new.html", new_context(request, f=blank_form()))


@router.post("/new")
def new_submit(request: Request, form: Annotated[NewProblemForm, Form()],
               db: Session = Depends(get_db)):
    """Create a problem — the single validated save path for BOTH the manual form
    and the AI review page (which posts here with source='ai' + its draft_id).

    Every field is validated before anything is written (validate_problem): slug
    format + collision, structure, canonical tags, statement/judge consistency, and
    the canonical passing all its tests in the sandbox. On any error the form is
    re-rendered with the messages and the author's exact input preserved — nothing
    reaches the DB or content/ until it is a coherent, verified problem.
    """
    source = form.source if form.source in ("manual", "ai") else "manual"
    is_ai = source == "ai"
    slug, draft_id = form.slug, form.draft_id
    raw = form.echo()

    def _reject(errors, warnings=None):  # noqa: ANN001
        # Recompute the AI-review extras so a failed Create still shows the banner,
        # collision hint, and similar-problem list.
        similar, collision, orig, suggested, gen, pending = [], False, "", "", {}, 0
        if is_ai:
            ex = existing_slugs(db)
            collision = bool(slug) and slug in ex
            orig, suggested = slug, (suggest_slug(slug, ex) if collision else "")
            similar = find_similar_problems(
                db, slug=slug, title=form.title,
                tags=[t.strip() for t in form.topics.split(",") if t.strip()])
            draft = draft_store.get(draft_id) if draft_id else None
            gen = (draft or {}).get("_validation", {})
            pending = len(draft_store.items())
        return templates.TemplateResponse(request, "admin/new.html", new_context(
            request, f=raw, errors=errors, warnings=warnings, ai=is_ai,
            draft_id=draft_id, source=source, collision=collision,
            original_slug=orig, suggested_slug=suggested, similar=similar,
            generation=gen, pending_count=pending), status_code=400)

    # Build the internal dict (bad test JSON fails here, before validation).
    try:
        data = to_data(form, slug=slug, source=source)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return _reject([f"Tests must be a valid JSON array of test objects: {exc}"])

    result = validate_problem(data, db=db, is_new=True)
    if not result.ok:
        return _reject(result.errors, result.warnings)

    prob, mirror_error = _save(db, data)
    if draft_id:
        draft_store.pop(draft_id)  # confirmed → drop the pending draft
    if mirror_error:
        # Created, but not on disk: land on the edit form with the warning rather
        # than redirecting to a page that would look like an unqualified success.
        return _edit_page(request, to_form(prob), saved=True,
                          warnings=[*result.warnings, mirror_error])
    return RedirectResponse(f"/admin/problems/{prob.slug}/edit", status_code=303)
