"""Admin: list problems, view/edit a problem's source, add one, or AI-generate.

No real auth (this is a home/LAN instance). If you expose lootcode beyond a
trusted network, put this router behind authentication.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import content, store
from ..config import settings
from ..db import get_db
from ..executor import run_submission
from ..models import Problem
from ..templating import templates

router = APIRouter(prefix="/admin")

COMPARE_MODES = ("exact", "unordered", "set_of_lists")


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


def _form_to_data(*, slug, title, difficulty, topics, statement_md, function_name,
                  params, return_type, compare, starter_code, canonical_solution,
                  tests_json, source) -> dict:
    tests = json.loads(tests_json)
    if not isinstance(tests, list) or not tests:
        raise ValueError("Tests must be a non-empty JSON array.")
    return {
        "slug": slug.strip(), "title": title.strip(), "difficulty": difficulty,
        "topics": [t.strip() for t in topics.split(",") if t.strip()],
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


# --- list -----------------------------------------------------------------
@router.get("")
def dashboard(request: Request, db: Session = Depends(get_db)):
    problems = list(db.scalars(select(Problem).order_by(Problem.id)))
    return templates.TemplateResponse(request, "admin/index.html", {
        "request": request, "problems": problems, "user_name": request.state.user_name,
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
        "error": None, "saved": False,
    })


@router.post("/problems/{slug}/edit")
def edit_submit(
    slug: str, request: Request, db: Session = Depends(get_db),
    title: str = Form(...), difficulty: str = Form("easy"), topics: str = Form(""),
    statement_md: str = Form(""), function_name: str = Form(...), params: str = Form(""),
    return_type: str = Form(""), compare: str = Form("exact"),
    starter_code: str = Form(""), canonical_solution: str = Form(""),
    tests_json: str = Form("[]"),
):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        data = _form_to_data(
            slug=slug, title=title, difficulty=difficulty, topics=topics,
            statement_md=statement_md, function_name=function_name, params=params,
            return_type=return_type, compare=compare, starter_code=starter_code,
            canonical_solution=canonical_solution, tests_json=tests_json,
            source=prob.source,  # preserve original source
        )
        _save(db, data)
        prob = db.scalar(select(Problem).where(Problem.slug == slug))
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return templates.TemplateResponse(request, "admin/edit.html", {
            "request": request, "user_name": request.state.user_name,
            "f": {**_form_view(prob), "title": title, "difficulty": difficulty,
                  "topics": topics, "statement_md": statement_md,
                  "function_name": function_name, "params": params,
                  "return_type": return_type, "compare": compare,
                  "starter_code": starter_code, "canonical_solution": canonical_solution,
                  "tests_json": tests_json},
            "compare_modes": COMPARE_MODES, "error": f"Could not save: {exc}",
            "saved": False,
        }, status_code=400)
    return templates.TemplateResponse(request, "admin/edit.html", {
        "request": request, "user_name": request.state.user_name,
        "f": _form_view(prob), "compare_modes": COMPARE_MODES, "error": None, "saved": True,
    })


# --- run a solution against the current (unsaved) tests --------------------
class VerifyBody(BaseModel):
    code: str
    function_name: str
    params: str = ""
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
    return templates.TemplateResponse(request, "admin/new.html", {
        "request": request, "user_name": request.state.user_name,
        "compare_modes": COMPARE_MODES, "error": None,
    })


@router.post("/new")
def new_submit(
    request: Request, db: Session = Depends(get_db),
    slug: str = Form(...), title: str = Form(...), difficulty: str = Form("easy"),
    topics: str = Form(""), statement_md: str = Form(""),
    function_name: str = Form(...), params: str = Form(""), return_type: str = Form(""),
    compare: str = Form("exact"), starter_code: str = Form(""),
    canonical_solution: str = Form(""), tests_json: str = Form("[]"),
):
    try:
        data = _form_to_data(
            slug=slug, title=title, difficulty=difficulty, topics=topics,
            statement_md=statement_md, function_name=function_name, params=params,
            return_type=return_type, compare=compare, starter_code=starter_code,
            canonical_solution=canonical_solution, tests_json=tests_json, source="manual")
        prob = _save(db, data)
    except (ValueError, KeyError, json.JSONDecodeError) as exc:
        return templates.TemplateResponse(request, "admin/new.html", {
            "request": request, "user_name": request.state.user_name,
            "compare_modes": COMPARE_MODES, "error": f"Could not save: {exc}",
        }, status_code=400)
    return RedirectResponse(f"/admin/problems/{prob.slug}/edit", status_code=303)


# --- AI generation --------------------------------------------------------
@router.get("/generate")
def generate_form(request: Request):
    return templates.TemplateResponse(request, "admin/generate.html", {
        "request": request, "user_name": request.state.user_name,
        "disabled": not settings.ai_enabled, "results": None, "error": None,
    })


@router.post("/generate")
def generate_submit(
    request: Request, db: Session = Depends(get_db),
    brief: str = Form(""), difficulty: str = Form(""),
    bulk_text: str = Form(""), count: int = Form(3),
):
    if not settings.ai_enabled:
        raise HTTPException(status_code=400, detail="AI generation is not configured.")
    from ..llm import generator

    results, error = [], None
    try:
        if bulk_text.strip():
            datas = generator.generate_from_text(bulk_text, count)
        elif brief.strip():
            datas = [generator.generate_problem(brief, difficulty or None)]
        else:
            datas = []
            error = "Enter a problem idea or paste source material."
        for data in datas:
            prob = _save(db, data)
            results.append({"slug": prob.slug, "title": prob.title,
                            "validation": data.get("_validation", {})})
    except Exception as exc:  # noqa: BLE001 - surface any generation/parse error
        error = f"Generation failed: {exc}"

    return templates.TemplateResponse(request, "admin/generate.html", {
        "request": request, "user_name": request.state.user_name,
        "disabled": False, "results": results, "error": error,
    })
