"""Marshalling between the admin HTML form and the internal problem dict.

One structure — the sixteen editable fields of a problem — used to be written
out five separate times in `routers/admin.py`: once to declare each save
route's body, once to serialize an ORM `Problem` into the edit form, once to
serialize a plain dict (an AI draft) into the same form, once for a blank form,
and once more as the `typed` dict that echoes a rejected edit back. Adding a
field meant finding all five, and missing one lost that field silently on the
path you forgot — a rejected save that quietly dropped the author's work.

Now there is one declaration (`ProblemForm`) and one serializer (`to_form`),
which takes either an ORM row or a dict.
"""
from __future__ import annotations

import json

from fastapi import Request
from pydantic import BaseModel

from .. import content
from ..config import settings

COMPARE_MODES = ("exact", "unordered", "set_of_lists")
KINDS = ("function", "class")


class ProblemForm(BaseModel):
    """Every editable field of a problem, exactly as the browser posts it.

    The request body of both save routes (`POST /admin/new` and
    `POST /admin/problems/{slug}/edit`). Every field has a default and every
    field is a string: the form is validated by `problem_validation`, which
    reports errors back into the page, so nothing here should 422 before the
    author's input has been echoed back to them.
    """

    # The edit form posts no slug — there the slug is the identity and arrives
    # as a path parameter — so this is empty on that route and supplied by hand.
    slug: str = ""
    title: str = ""
    difficulty: str = "easy"
    topics: str = ""
    hints: str = ""
    statement_md: str = ""
    kind: str = "function"
    function_name: str = ""
    params: str = ""
    return_type: str = ""
    class_name: str = ""
    class_methods_json: str = "[]"
    compare: str = "exact"
    starter_code: str = ""
    canonical_solution: str = ""
    tests_json: str = "[]"

    def echo(self, *, slug: str | None = None) -> dict:
        """Exactly what the author typed, for re-rendering a rejected save.

        Deliberately *not* round-tripped through `to_data`/`to_form`: a save can
        be rejected because the test JSON does not parse, and the author needs
        their own broken text back to fix, not a normalized version of it.

        Only the editable fields, never a subclass's extras — the result is bound
        straight into the form template.
        """
        typed = {name: getattr(self, name) for name in ProblemForm.model_fields}
        return typed if slug is None else {**typed, "slug": slug}


class NewProblemForm(ProblemForm):
    """The create route's body: the problem, plus where it came from.

    Separate from `ProblemForm` rather than two extra `Form(...)` parameters on
    the handler, because FastAPI flattens a form model's fields into the body
    only when it is the *sole* body parameter — add a scalar alongside it and
    every field silently has to arrive nested under `form`, which is a 422 for
    the browser that posts the flat form.
    """

    #: 'manual' | 'ai' — the AI review page posts back through this same route.
    source: str = "manual"
    #: Set by the AI review page so a confirmed draft can be dropped.
    draft_id: str = ""


def parse_params(text: str) -> list[dict]:
    """`name: type` per line -> the params list. An omitted type means `any`."""
    out = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        name, _, typ = line.partition(":")
        out.append({"name": name.strip(), "type": typ.strip() or "any"})
    return out


def to_data(form: ProblemForm, *, slug: str, source: str) -> dict:
    """Form -> the internal problem dict that `validate_problem` and the store take.

    `slug` is passed in rather than read off the form because the edit route
    takes it from the path. Raises `ValueError`/`JSONDecodeError` on malformed
    test or class-method JSON, which the caller turns into a form error.
    """
    tests = json.loads(form.tests_json)
    if not isinstance(tests, list) or not tests:
        raise ValueError("Tests must be a non-empty JSON array.")
    kind = form.kind if form.kind in KINDS else "function"
    data = {
        "slug": slug.strip(), "title": form.title.strip(),
        "difficulty": form.difficulty,
        "topics": [t.strip() for t in form.topics.split(",") if t.strip()],
        # One hint per line; normalize_hints trims blanks and caps at MAX_HINTS.
        "hints": content.normalize_hints(form.hints.splitlines()),
        "statement_md": form.statement_md,
        # For a class problem the params textarea holds the *constructor* params.
        "params": parse_params(form.params),
        "compare": form.compare if form.compare in COMPARE_MODES else "exact",
        "starter_code": form.starter_code,
        "canonical_solution": form.canonical_solution or None,
        "scoring_type": "weighted", "points": 100, "source": source, "kind": kind,
        "time_limit_ms": settings.EXEC_TIME_LIMIT_MS,
        "memory_limit_mb": settings.EXEC_MEMORY_LIMIT_MB, "tests": tests,
    }
    if kind == "class":
        methods = json.loads(form.class_methods_json or "[]")
        if not isinstance(methods, list):
            raise ValueError("Class methods must be a JSON array of method objects.")
        data.update(function_name="", return_type="",
                    class_name=form.class_name.strip(), class_methods=methods)
    else:
        data.update(function_name=form.function_name.strip(),
                    return_type=form.return_type.strip(),
                    class_name=None, class_methods=None)
    return data


def _fields(src) -> dict:  # noqa: ANN001
    """The problem's fields as a plain mapping, from an ORM row or a dict.

    The two sources are the stored problem (edit) and an AI-generated draft
    (review); everything downstream of here is identical for both, which is the
    point — the two used to be separate near-copies that had already drifted in
    how defensively they handled missing values.
    """
    if isinstance(src, dict):
        return src
    return {
        "slug": src.slug, "title": src.title, "difficulty": src.difficulty,
        "topics": src.topics, "hints": src.hints,
        "statement_md": src.statement_md,
        "kind": getattr(src, "kind", "function"),
        "function_name": src.function_name, "params": src.params,
        "return_type": src.return_type,
        "class_name": getattr(src, "class_name", ""),
        "class_methods": getattr(src, "class_methods", None),
        "compare": src.compare, "starter_code": src.starter_code,
        "canonical_solution": src.canonical_solution,
        "tests": [{"name": t.name, "input": t.input, "expected": t.expected,
                   "weight": t.weight, "hidden": t.hidden} for t in src.tests],
    }


def to_form(src) -> dict:  # noqa: ANN001
    """Serialize a stored problem (ORM row) or a draft (dict) into form strings."""
    d = _fields(src)
    params = [p for p in (d.get("params") or [])
              if isinstance(p, dict) and p.get("name")]
    return {
        "slug": d.get("slug") or "", "title": d.get("title") or "",
        "difficulty": d.get("difficulty") or "easy",
        "topics": ", ".join(d.get("topics") or []),
        "hints": "\n".join(d.get("hints") or []),
        "statement_md": d.get("statement_md") or "",
        "kind": d.get("kind") or "function",
        "function_name": d.get("function_name") or "",
        "params": "\n".join(f"{p['name']}: {p.get('type', 'any')}" for p in params),
        "return_type": d.get("return_type") or "",
        "class_name": d.get("class_name") or "",
        "class_methods_json": json.dumps(d.get("class_methods") or [], indent=2),
        "compare": d.get("compare") or "exact",
        "starter_code": d.get("starter_code") or "",
        "canonical_solution": d.get("canonical_solution") or "",
        "tests_json": json.dumps(
            [{"name": t.get("name"), "input": t.get("input"),
              "expected": t.get("expected"), "weight": t.get("weight", 1),
              "hidden": t.get("hidden", False)} for t in (d.get("tests") or [])],
            indent=2),
    }


# The starter example shown in an empty "New problem" form (bound as the tests
# field's initial value so the author sees the exact shape a test case takes).
_EXAMPLE_TESTS_JSON = """[
  {"name": "example-1", "input": {"s": "hello"}, "expected": "olleh", "weight": 1, "hidden": false},
  {"name": "hidden-1", "input": {"s": ""}, "expected": "", "weight": 1, "hidden": true}
]"""


def blank_form() -> dict:
    """Field values for a fresh New-problem form: the posted defaults, except
    that the tests box shows a worked example rather than an empty array."""
    return {**ProblemForm().model_dump(), "tests_json": _EXAMPLE_TESTS_JSON}


def new_context(request: Request, *, f: dict, errors=None, warnings=None,  # noqa: ANN001
                ai: bool = False, draft_id: str = "", source: str = "manual",
                collision: bool = False, original_slug: str = "",
                suggested_slug: str = "", similar=None, generation=None,  # noqa: ANN001
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
