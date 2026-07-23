"""Pre-save validation shared by the manual-create and AI-review admin flows.

Both the "New problem (manual)" form and the AI "review before save" step push a
problem through the SAME gate before it is written to the DB / ``content/``. Until
this module existed, the admin add/generate paths saved whatever they were handed —
a bad slug, an invented tag, a canonical that never runs, tests that don't match
the signature — with no feedback. This is the gate that stops that.

What it checks, cheapest → most expensive (first failures short-circuit later,
more costly steps for a given field):

  * **SLUG** — lowercase kebab-case, and (for a new problem) not already taken, so
    authoring/generation can never silently overwrite an existing problem.
  * **STRUCTURAL** — reuses ``scripts/test_llm_output.py`` (strict pydantic + static
    ``ast``): valid identifiers, canonical/starter parse and define the declared
    function with exactly the declared params, each test's ``input`` keys equal the
    param names, ``expected`` shape matches the compare mode, enough/unique tests,
    JSON-serializable values. It **never executes code** (AST only), so it is safe
    to run inside the web process.
  * **TAGS** — every tag must be canonical (``app/tags.py``). Known aliases fold on
    write and are reported; a genuinely unknown tag is rejected — the interactive
    author is right here to fix it, unlike the advisory bulk importer.
  * **CONSISTENCY** — a statement promising "any order" must not pair with
    ``compare=exact`` (pure text check, mirrors ``scripts/audit.py``).
  * **BEHAVIORAL** — the canonical solution must pass **all** its own tests in the
    real sandbox (``app.executor.run_submission``). This is the one authoritative
    "is this problem actually correct" check, and it is the last step so we never
    spin up the sandbox for a structurally broken problem.

Security note: we deliberately do **not** call ``scripts/audit.py``'s in-process
fairness step — it ``exec()``s the (possibly AI-authored) canonical in the current
process, which would break the sandbox guarantee (docs/code-execution.md). The
behavioral check above already runs the canonical in the sandbox; the consistency
check here is pure string work.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from math import log
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .executor import run_submission
from .models import Problem
from .tags import (
    CANONICAL_TAGS,
    DROPPED_TAGS,
    TAG_ALIASES,
    normalize_tags,
    unknown_tags,
)

# Reuse the project's standalone structural validator (pydantic + static AST). It
# NEVER executes code, imports nothing from ``app``, and is the exact gate
# scripts/import_generated_problems.py uses — so structural rules stay defined in
# one place.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
import test_llm_output as _tlo  # noqa: E402

COMPARE_MODES = ("exact", "unordered", "set_of_lists")

# A slug is the durable identity + on-disk directory name: strict kebab-case.
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")

# "Any order" language that must not pair with compare=exact (mirrors scripts/audit.py).
_AMBIGUITY = ("any order", "in any order", "any valid", "you may return",
              "return any", "multiple valid")

# Type labels are DOCUMENTATION only (passed through as plain JSON) — except the
# rich types, which are load-bearing (the harness builds real objects for them).
# We never block on a type label, but we nudge toward the house spelling and flag a
# label that is neither a known scalar/array nor a rich type (a likely typo, e.g.
# "TreeNod", which would silently be treated as a plain value and break decoding).
_RICH_TYPES = frozenset({"TreeNode", "ListNode", "DoublyLinkedList"})
# Helper types the harness injects for class-based ("design") problems — a class
# constructor/method may take an Iterator or a nested-list of NestedInteger.
_HELPER_TYPES = frozenset({
    "Iterator", "Iterator<int>", "NestedInteger", "NestedInteger[]",
    "List<NestedInteger>",
})
_BASE_TYPES = frozenset({
    "int", "float", "bool", "string", "char", "any", "void", "none", "object",
})
# Common non-house spellings → the house style, surfaced as a gentle warning.
_HOUSE_STYLE = {"str": "string", "integer": "int", "boolean": "bool",
                "double": "float", "number": "float", "list": "<elem>[]",
                "dict": "object", "null": "any", "none": "any"}


@dataclass
class ValidationResult:
    """Outcome of :func:`validate_problem`. ``errors`` block the save; ``warnings``
    inform but never block. ``solved``/``behavioral`` are populated only when the
    sandbox behavioral check ran (structure was sound enough to bother)."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    behavioral: str = ""           # e.g. "8/8 tests passed"; "" if the check didn't run
    solved: bool | None = None     # None if the behavioral check didn't run

    @property
    def ok(self) -> bool:
        return not self.errors


# ---------------------------------------------------------------------------
# The core gate.
# ---------------------------------------------------------------------------
def validate_problem(data: dict, *, db: Session | None = None, is_new: bool = True,
                     run_behavioral: bool = True) -> ValidationResult:
    """Validate an internal problem dict (the shape ``_form_to_data`` produces).

    ``is_new`` enables the slug-collision check (skip it when editing in place).
    ``db`` is needed for the collision check; ``run_behavioral`` runs the canonical
    in the sandbox (the slow, authoritative step) once the structure is sound.
    """
    res = ValidationResult()

    slug = (data.get("slug") or "").strip()
    title = (data.get("title") or "").strip()

    # --- slug + title --------------------------------------------------------
    if not slug:
        res.errors.append("A slug is required (the problem's durable identity).")
    elif not SLUG_RE.match(slug):
        res.errors.append(
            f"Slug {slug!r} must be lowercase kebab-case: letters, digits and single "
            "hyphens only, with no leading or trailing hyphen (e.g. 'reverse-string').")
    if not title:
        res.errors.append("A title is required.")

    # --- structural (static, safe) ------------------------------------------
    core = _core_contract(data)
    rep = _tlo.validate(core, strict=False)
    res.errors.extend(_friendlier(e) for e in rep.errors)
    # tlo also warns about non-canonical tags, but our tag gate below is stricter and
    # gives a better message — drop tlo's version to avoid a confusing duplicate.
    res.warnings.extend(w for w in rep.warnings
                        if not w.lstrip().lower().startswith("tags:"))

    # --- tags: canonical only (hard) ----------------------------------------
    topics = [t for t in (data.get("topics") or []) if str(t).strip()]
    unknown = unknown_tags(topics)
    if unknown:
        res.errors.append(
            f"Tag(s) {unknown} are not in the canonical vocabulary and are not known "
            "aliases. Use only canonical tags (an alias like 'bfs' or 'dfs' is fine — "
            "it folds automatically). Allowed tags: "
            f"{', '.join(sorted(CANONICAL_TAGS))}.")
    folds = {}
    for t in topics:
        low = str(t).strip().lower()
        if low in TAG_ALIASES:
            folds[low] = TAG_ALIASES[low]
    if folds:
        res.warnings.append(
            "These tags fold to their canonical form on save: "
            + ", ".join(f"'{k}' → '{v}'" for k, v in folds.items()) + ".")
    dropped = sorted({str(t).strip().lower() for t in topics
                      if str(t).strip().lower() in DROPPED_TAGS})
    if dropped:
        res.warnings.append(f"These tags are too vague and will be dropped on save: "
                            f"{dropped}.")

    # --- type-label house-style nudges (soft) -------------------------------
    for label, typ in _iter_types(data):
        note = _type_note(label, typ)
        if note:
            res.warnings.append(note)

    # --- statement ↔ compare consistency (text, safe) -----------------------
    if data.get("compare") == "exact":
        text = " ".join((data.get("statement_md") or "").lower().split())
        if any(kw in text for kw in _AMBIGUITY):
            res.errors.append(
                "The statement says the answer may be in 'any order', but compare is "
                "'exact' — the judge would reject a valid re-ordering. Set compare to "
                "'unordered' or 'set_of_lists', or pin the exact order in the statement.")

    # --- slug collision (new problems only) ---------------------------------
    if is_new and slug and SLUG_RE.match(slug):
        existing = existing_slugs(db)
        if slug in existing:
            res.errors.append(
                f"A problem with slug {slug!r} already exists — saving would overwrite "
                f"it. Choose a different slug (e.g. {suggest_slug(slug, existing)!r}), "
                "or edit the existing problem directly.")

    # --- behavioral (sandboxed) — only if the structure is otherwise sound ---
    canonical = (data.get("canonical_solution") or "").strip()
    if run_behavioral and canonical and not res.errors:
        g = _run_canonical(data)
        res.solved = g.solved
        res.behavioral = f"{g.passed_count}/{g.total_count} tests passed"
        if not g.solved:
            res.errors.append(
                "The canonical solution does not pass all of its own tests "
                f"({res.behavioral}). It must pass every test before the problem can be "
                "saved. Failing: " + _failing_detail(g))

    return res


# ---------------------------------------------------------------------------
# Similar-problem suggestions (a "please confirm this isn't a duplicate" nudge).
# There is no near-duplicate detector in the codebase yet (see
# docs/duplicate-detection-plan.md); this is a cheap token/tag-overlap heuristic,
# surfaced for the human to eyeball — never a hard gate.
# ---------------------------------------------------------------------------
def _raw_tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def _stem(w: str) -> str:
    """A deliberately small, conservative stemmer: collapse the inflections that
    otherwise hide near-duplicates — plurals and the adjective/noun split
    (``palindromic``/``palindrome``/``palindromes`` → ``palindrom``,
    ``subsequences``/``subsequence`` → ``subsequenc``, ``strings`` → ``string``).

    It intentionally does NOT strip ``-ing``/``-ed`` (which would mangle common
    content words like ``string`` → ``str``); the goal is unifying obvious variants,
    not linguistic correctness. Over-stemming risks false matches, so we keep it
    minimal and let IDF weighting do the discriminating.
    """
    if len(w) <= 3:
        return w
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"          # queries -> query
    elif w.endswith("es") and len(w) > 4 and not w.endswith(("ses", "zes")):
        w = w[:-2]                # boxes -> box, palindromes -> palindrom
    elif w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]                # strings -> string (class stays class)
    if w.endswith("ical") and len(w) > 5:
        w = w[:-4]
    elif w.endswith("ic") and len(w) > 4:
        w = w[:-2]                # palindromic -> palindrom
    if len(w) > 3 and w.endswith("e"):
        w = w[:-1]                # palindrome -> palindrom, subsequence -> subsequenc
    return w


# Genuine function words that carry no "is this the same problem" signal. IDF
# weighting (below) already demotes anything common, so this set only needs the
# truly ubiquitous glue words; content words like "two", "sum", "array", "tree"
# must NOT be here (that was what hid "Two Sum" from its own near-duplicates).
_STOPWORDS = frozenset({
    "the", "a", "an", "of", "to", "and", "or", "in", "on", "with", "for", "is",
    "are", "be", "as", "at", "by", "from", "that", "this", "it", "its", "if",
    "you", "your", "given", "find", "problem", "all", "each", "every", "any",
})


def _stemmed_tokens(*parts: str) -> set[str]:
    """Stemmed, stop-word-filtered token set for one or more strings (slug, title)."""
    out = set()
    for p in parts:
        for w in _raw_tokens(p):
            if w in _STOPWORDS:
                continue
            out.add(_stem(w))
    return out


def find_similar_problems(db: Session, *, slug: str, title: str,
                          tags: list[str] | None, limit: int = 5) -> list[dict]:
    """Existing problems that look like they might be the same problem.

    Scored by shared slug/title tokens weighted by **inverse document frequency**
    (a token shared by half the bank — "number", "string", "count" — barely counts;
    a rare one — "palindrom", "subsequenc" — counts a lot), plus a small bump for
    shared canonical tags. Tokens are stemmed first, so "palindromic subsequences"
    matches "palindromic subsequence". Requires at least one shared meaningful token
    so a purely tag-matching flood is excluded. Returns up to ``limit`` dicts: slug,
    title, difficulty, shared_tags, matched (the overlapping stems), most-similar
    first.
    """
    if db is None:
        return []
    want_tokens = _stemmed_tokens(slug, title)
    want_tags = set(normalize_tags(tags)) if tags else set()
    rows = db.execute(
        select(Problem.slug, Problem.title, Problem.topics, Problem.difficulty)).all()

    # Document frequency of each stem across the bank, so a token's weight reflects
    # how discriminating it is (rare = informative). Computed once per call — the
    # bank is at most a few thousand rows, so this is a handful of milliseconds.
    others = [(s, t, topics, diff) for s, t, topics, diff in rows if s != slug]
    n = len(others) or 1
    df: dict[str, int] = {}
    their_tokens_by_slug: dict[str, set[str]] = {}
    for s, t, _topics, _diff in others:
        toks = _stemmed_tokens(s, t)
        their_tokens_by_slug[s] = toks
        for w in toks:
            df[w] = df.get(w, 0) + 1

    def idf(tok: str) -> float:
        # Smoothed IDF: 0 for a token in every problem, growing as it gets rarer.
        return log((n + 1) / (df.get(tok, 0) + 1)) + 1.0

    scored = []
    for s, t, topics, diff in others:
        shared_tokens = want_tokens & their_tokens_by_slug[s]
        if not shared_tokens:
            continue  # require a real name overlap, not just a shared tag
        shared_tags = want_tags & set(topics or [])
        # Weight name overlap by IDF; give tags a modest fixed nudge (they're broad).
        score = sum(idf(w) for w in shared_tokens) + 0.75 * len(shared_tags)
        scored.append((score, s, {
            "slug": s, "title": t, "difficulty": diff,
            "shared_tags": sorted(shared_tags),
            "matched": sorted(shared_tokens),
        }))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [d for _, _, d in scored[:limit]]


# ---------------------------------------------------------------------------
# Slug helpers.
# ---------------------------------------------------------------------------
def existing_slugs(db: Session | None) -> set[str]:
    """Every slug already claimed — in the DB (runtime source of truth) and on disk
    under either content root — so a new slug avoids clobbering a real problem even
    if it is present on disk but not yet seeded."""
    slugs: set[str] = set()
    if db is not None:
        slugs |= {row[0] for row in db.execute(select(Problem.slug)).all()}
    for base in settings.content_dirs:
        if base.is_dir():
            slugs |= {p.name for p in base.iterdir()
                      if p.is_dir() and (p / "meta.json").exists()}
    return slugs


def suggest_slug(slug: str, existing: set[str]) -> str:
    """A free slug near ``slug`` (append -2, -3, …). Falls back to the original."""
    if slug not in existing:
        return slug
    for n in range(2, 100):
        cand = f"{slug}-{n}"
        if cand not in existing:
            return cand
    return slug


# ---------------------------------------------------------------------------
# Internals.
# ---------------------------------------------------------------------------
def _core_contract(data: dict) -> dict:
    """Adapt the internal problem dict into the "core contract" shape
    ``test_llm_output.validate`` expects (``tags`` not ``topics``; no slug/title/
    statement). Fills weight/hidden/name defaults so the structural gate doesn't
    reject a hand-authored test merely for omitting an optional field."""
    tests = []
    for i, t in enumerate(data.get("tests") or []):
        if isinstance(t, dict):
            t = dict(t)
            t.setdefault("name", f"test-{i + 1}")
            t.setdefault("weight", 1)
            t.setdefault("hidden", False)
        tests.append(t)
    kind = data.get("kind", "function") or "function"
    core = {
        "kind": kind,
        "difficulty": data.get("difficulty", "easy"),
        "tags": data.get("topics", []) or [],
        "params": data.get("params", []) or [],
        "compare": data.get("compare", "exact") or "exact",
        "starter_code": data.get("starter_code", "") or "",
        "canonical_solution": data.get("canonical_solution", "") or "",
        "tests": tests,
    }
    if kind == "class":
        core["class_name"] = data.get("class_name", "") or ""
        core["class_methods"] = data.get("class_methods", []) or []
    else:
        core["function_name"] = data.get("function_name", "") or ""
        core["return_type"] = data.get("return_type", "") or ""
    return core


def _friendlier(err: str) -> str:
    """Rewrite the two most common terse pydantic messages into plain guidance."""
    if "canonical_solution" in err and "string_too_short" in err:
        return ("A canonical solution is required — the problem can't be verified "
                "without a reference solution that passes every test.")
    if "starter_code" in err and "string_too_short" in err:
        return ("Starter code is required — provide the function stub shown to solvers "
                "(the signature with a docstring/`pass`, no solution).")
    return f"structural: {err}"


def _iter_types(data: dict):
    """Yield ('<label>', <type>) for each type label declared in the problem, for
    the house-style nudge — the function's params/return, or (for a class problem)
    the constructor params and every method's params and return."""
    if (data.get("kind") or "function") == "class":
        for p in data.get("params") or []:
            if isinstance(p, dict):
                yield f"constructor parameter '{p.get('name', '?')}'", p.get("type", "")
        for m in data.get("class_methods") or []:
            if not isinstance(m, dict):
                continue
            mname = m.get("name", "?")
            yield f"method '{mname}' return", (m.get("returns") or {}).get("type", "")
            for p in m.get("params") or []:
                if isinstance(p, dict):
                    yield (f"method '{mname}' parameter '{p.get('name', '?')}'",
                           p.get("type", ""))
        return
    yield "return type", data.get("return_type", "")
    for p in data.get("params") or []:
        if isinstance(p, dict):
            yield f"parameter '{p.get('name', '?')}'", p.get("type", "")


def _type_note(label: str, typ: str) -> str | None:
    t = (typ or "").strip()
    if not t:
        return None
    if t in _HELPER_TYPES:
        return None
    base = t.rstrip("[]") or t  # strip array suffixes: "int[]" -> "int"
    if base in _RICH_TYPES or base in _HELPER_TYPES:
        return None
    low = base.lower()
    if low in _HOUSE_STYLE:
        return (f"{label} type {t!r}: the house style writes this as "
                f"'{_HOUSE_STYLE[low]}' (type labels are documentation only, so this "
                "won't block saving).")
    if low not in _BASE_TYPES:
        return (f"{label} type {t!r} is unusual — type labels are documentation only "
                f"except the rich types {sorted(_RICH_TYPES)}; double-check the spelling.")
    return None


def _run_canonical(data: dict):
    """Run the canonical solution against the problem's tests in the real sandbox."""
    compare = data.get("compare", "exact")
    prob = SimpleNamespace(
        kind=data.get("kind", "function") or "function",
        function_name=(data.get("function_name") or "").strip(),
        params=data.get("params", []) or [],
        return_type=(data.get("return_type") or "").strip(),
        class_name=data.get("class_name"),
        class_methods=data.get("class_methods"),
        compare=compare if compare in COMPARE_MODES else "exact",
        time_limit_ms=data.get("time_limit_ms", settings.EXEC_TIME_LIMIT_MS),
        memory_limit_mb=data.get("memory_limit_mb", settings.EXEC_MEMORY_LIMIT_MB),
        points=data.get("points", 100),
    )
    tests = [
        SimpleNamespace(
            name=t.get("name", f"test-{i + 1}"), input=t.get("input", {}),
            expected=t.get("expected"), weight=t.get("weight", 1),
            hidden=t.get("hidden", False))
        for i, t in enumerate(data.get("tests", []) or [])
    ]
    return run_submission(data.get("canonical_solution") or "", prob, tests)


def _failing_detail(g) -> str:
    """Compact per-failing-test summary for the error message."""
    bits = []
    for r in g.results:
        if getattr(r, "passed", False):
            continue
        piece = f"{r.name} [{r.status}]"
        if getattr(r, "error", None):
            piece += f": {str(r.error).splitlines()[-1][:120]}"
        bits.append(piece)
    return "; ".join(bits) if bits else "(see the Run panel for detail)"
