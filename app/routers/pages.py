"""Server-rendered pages: problem list, problem detail, and per-user progress."""
from __future__ import annotations

import math
import os
import random
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, unquote, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import progress, store
from ..config import settings
from ..db import get_db
from ..models import Collection, Problem, Submission, User
from ..pagination import page_window
from ..templating import templates

router = APIRouter()

# Read-only helper definitions surfaced next to the function signature when a
# problem declares a rich input/return type, so solvers know the object shape.
# The harness injects the real class (see app/executor/harness.py); this is just
# the documentation shown in the UI. Keep the shape in sync with that class.
PROVIDED_TYPE_DEFS = {
    "TreeNode": (
        "class TreeNode:  # binary tree node — provided, do not redefine\n"
        "    def __init__(self, value=None, left=None, right=None):\n"
        "        self.value = value\n"
        "        self.left = left\n"
        "        self.right = right"
    ),
    "ListNode": (
        "class ListNode:  # singly-linked list node — provided, do not redefine\n"
        "    def __init__(self, val=0, next=None):\n"
        "        self.val = val\n"
        "        self.next = next"
    ),
    "DoublyLinkedList": (
        "class Node:  # doubly-linked list node — provided, do not redefine\n"
        "    def __init__(self, val=0, prev=None, next=None):\n"
        "        self.val = val\n"
        "        self.prev = prev\n"
        "        self.next = next"
    ),
    # Helper types the harness injects for class-based ("design") problems whose
    # constructor/method takes one (see app/executor/harness.py).
    "Iterator": (
        "class Iterator:  # provided, do not redefine\n"
        "    def hasNext(self) -> bool: ...  # another element remains?\n"
        "    def next(self) -> int: ...      # return the next element, advance"
    ),
    "NestedInteger": (
        "class NestedInteger:  # provided, do not redefine\n"
        "    def isInteger(self) -> bool: ...  # holds a single integer?\n"
        "    def getInteger(self) -> int: ...  # the integer (else None)\n"
        "    def getList(self) -> list: ...     # the nested list (else None)"
    ),
}
# Type-label aliases that map onto the same provided-type definition.
PROVIDED_TYPE_DEFS["Iterator<int>"] = PROVIDED_TYPE_DEFS["Iterator"]
for _alias in ("List<NestedInteger>", "NestedInteger[]"):
    PROVIDED_TYPE_DEFS[_alias] = PROVIDED_TYPE_DEFS["NestedInteger"]


def _provided_types(prob) -> dict:
    """Ordered map of declared custom type -> its definition snippet, for the
    rich/helper types this problem actually uses. Covers a function's params and
    return, and (for a class problem) the constructor params plus every method's
    params and return."""
    used: list[str] = [(p.get("type") or "") for p in (prob.params or [])]
    used.append(getattr(prob, "return_type", "") or "")
    for m in (getattr(prob, "class_methods", None) or []):
        used.extend((p.get("type") or "") for p in (m.get("params") or []))
        used.append((m.get("returns") or {}).get("type") or "")
    # De-dup by definition (aliases share one), preserving first-seen order.
    out: dict = {}
    seen: set = set()
    for t in used:
        defn = PROVIDED_TYPE_DEFS.get(t)
        if defn and defn not in seen:
            out[t] = defn
            seen.add(defn)
    return out


@router.get("/favicon.ico", include_in_schema=False)
def favicon():
    """Serve the site icon for clients that probe /favicon.ico directly.

    Pages advertise the SVG via <link rel="icon"> (see base.html); this is a
    fallback for the browser/credential-manager default probe so it gets a 200
    instead of guessing a (mangled) URL and 404ing."""
    return FileResponse(settings.STATIC_DIR / "favicon.svg",
                        media_type="image/svg+xml")


# The problem bank has grown large enough that one long list is unwieldy.
PROBLEMS_PER_PAGE = 25

# The category bar renders every topic chip and CSS clips it to one row, so how
# many are visible is a browser-side question. This is only the threshold for
# offering the "Expand" toggle at all: a deliberate under-estimate of how many
# chips fit on one row, so the toggle appears whenever there is certainly more.
TOPIC_BAR_TOGGLE_MIN = 8

# How many problems the "Recent submissions" list shows. The cap is per problem
# (each shown with its full attempt history), not per attempt.
RECENT_PROBLEMS_LIMIT = 25


def _user_tz(request: Request) -> ZoneInfo:
    """The visitor's timezone, from the client-set `lc_tz` cookie (falling back
    to UTC). The weekly grid buckets solves by the user's *local* day, so a
    late-night solve fills tonight's column instead of rolling into tomorrow's.

    The client sets the cookie via `encodeURIComponent`, so an IANA name like
    `America/New_York` arrives percent-encoded (`America%2FNew_York`); Starlette
    does not decode cookie values, so we `unquote` here before handing it to
    `ZoneInfo` — otherwise every slashed zone name silently fell back to UTC."""
    name = request.cookies.get("lc_tz")
    if name:
        try:
            return ZoneInfo(unquote(name))
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return ZoneInfo("UTC")


# Figures live at content/problems/<slug>/assets/<file> (see docs/problem-images.md).
# Only these image types are served; never the problem's solution/ or tests/.
_IMAGE_MEDIA = {
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
}


@router.get("/problems/{slug}/assets/{filename}")
def problem_asset(slug: str, filename: str):
    """Serve a problem figure. Deliberately narrow: only the per-problem `assets/`
    dir, only image extensions, and path-traversal is rejected.

    Searches **every** content root, not just ``CONTENT_DIR``. Problems live in
    two roots (the committed default set and the gitignored extended set, see
    ``settings.content_dirs``); resolving only the first made every figure in the
    extended set 404 while its statement still rendered the ``<img>``.
    """
    if any(bad in slug for bad in ("/", "\\", "..")) or \
       any(bad in filename for bad in ("/", "\\", "..")):
        raise HTTPException(status_code=404, detail="Not found")
    media_type = _IMAGE_MEDIA.get(Path(filename).suffix.lower())
    if media_type is None:
        raise HTTPException(status_code=404, detail="Not found")

    for root in settings.content_dirs:
        assets_dir = (root / slug / "assets").resolve()
        target = (assets_dir / filename).resolve()
        # Belt-and-suspenders: the resolved file must stay inside that assets dir.
        if os.path.commonpath([str(assets_dir), str(target)]) != str(assets_dir):
            continue
        if target.is_file():
            return FileResponse(target, media_type=media_type)
    raise HTTPException(status_code=404, detail="Not found")


@router.get("/")
def index(request: Request, difficulty: str | None = None, topic: str | None = None,
          q: str | None = None, collection: str | None = None, unsolved: int = 0,
          solved: int = 0, unknown: int = 0, known: int = 0, visit_later: int = 0,
          page: int = 1, db: Session = Depends(get_db)):
    stmt = select(Problem).where(Problem.is_published.is_(True))
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    if q:
        stmt = stmt.where(Problem.title.ilike(f"%{q}%"))
    problems = list(db.scalars(stmt.order_by(Problem.id)))
    if topic:
        problems = [p for p in problems if topic in (p.topics or [])]

    # Active curated list ("Blind 73", …). Resolve once to an ordered membership;
    # an unknown/stale slug is treated as no filter so a bad link isn't an empty
    # page. When active, the list is shown in its curated study order (position).
    active_collection = db.scalar(
        select(Collection).where(Collection.slug == collection)) if collection else None
    if active_collection is None:
        collection = None
    coll_order = {it.problem_id: it.position for it in active_collection.items} \
        if active_collection else {}
    if active_collection:
        problems = [p for p in problems if p.id in coll_order]

    solved_ids = store.user_solved_problem_ids(db, request.state.user_id)
    known_ids = store.user_known_problem_ids(db, request.state.user_id)
    visit_later_ids = store.user_visit_later_problem_ids(db, request.state.user_id)
    if unsolved:
        problems = [p for p in problems if p.id not in solved_ids]
    # "See all" from the My Progress summary links here with solved=1.
    if solved:
        problems = [p for p in problems if p.id in solved_ids]
    # "Unknown only" hides both explicitly-known problems and solved ones (a
    # solved problem is implicitly known — a UI rule, not stored that way).
    if unknown:
        problems = [p for p in problems
                    if p.id not in known_ids and p.id not in solved_ids]
    # "Known only" — the complement of `unknown`: show just the problems this user
    # has explicitly marked known. URL-only (no UI chip); combines with other filters.
    if known:
        problems = [p for p in problems if p.id in known_ids]
    # "Visit later" is an independent bookmark axis — it shows only flagged
    # problems and combines freely with every other filter (incl. the status
    # chips above), so it isn't part of their mutually-exclusive group.
    if visit_later:
        problems = [p for p in problems if p.id in visit_later_ids]

    # When a curated list is active, present it in its study order (position)
    # rather than by problem id.
    if active_collection:
        problems.sort(key=lambda p: coll_order[p.id])

    # Banner progress for the active list: solved/total for the whole collection
    # (its published members), plus an easy/medium/hard breakdown. Computed over
    # the full membership — independent of the difficulty/status/topic filters —
    # so the banner always describes the list as a whole, not the filtered view.
    coll_stats = None
    if active_collection:
        by_diff = {d: {"solved": 0, "total": 0} for d in ("easy", "medium", "hard")}
        for it in active_collection.items:
            prob = it.problem
            if prob is None or not prob.is_published or prob.difficulty not in by_diff:
                continue
            by_diff[prob.difficulty]["total"] += 1
            if prob.id in solved_ids:
                by_diff[prob.difficulty]["solved"] += 1
        coll_stats = {
            "total": sum(d["total"] for d in by_diff.values()),
            "solved": sum(d["solved"] for d in by_diff.values()),
            "by_difficulty": [
                {"name": name, "solved": d["solved"], "total": d["total"]}
                for name, d in by_diff.items()
            ],
        }

    # Category bar: published-problem count per topic, most-common first. Which
    # chips the collapsed bar clips away is decided by CSS, not here, so whenever
    # a topic filter is active we start expanded — that's the only way to be sure
    # the highlighted chip is on screen.
    topic_counts = progress.topic_counts(db)
    topic_expanded = bool(topic)

    # Counts per difficulty for the "jump to a random unsolved" buttons — skipping
    # solved *and* known so the count matches what the random jump can land on.
    unsolved_counts = progress.unsolved_counts(db, solved_ids | known_ids)

    # Filter chips are toggle links. Each href keeps the *other* active filters, so
    # a status (Unsolved/Unknown) and a topic combine in either click order; the
    # two status chips are mutually exclusive, and clicking an already-active chip
    # clears just that one filter. (Passing an override of None drops that key.)
    current = {
        "q": q, "difficulty": difficulty, "topic": topic, "collection": collection,
        "unsolved": 1 if unsolved else None,
        "unknown": 1 if unknown else None,
        "solved": 1 if solved else None,
        "visit_later": 1 if visit_later else None,
    }

    def _href(**overrides: object) -> str:
        qs = urlencode({k: v for k, v in {**current, **overrides}.items() if v})
        return f"/?{qs}" if qs else "/"

    unsolved_href = _href(unsolved=None) if unsolved \
        else _href(unsolved=1, unknown=None, solved=None)
    unknown_href = _href(unknown=None) if unknown \
        else _href(unknown=1, unsolved=None, solved=None)
    # "Visit later" toggles on its own and keeps every other active filter — it
    # doesn't clear the status chips (and they don't clear it).
    visit_later_href = _href(visit_later=None) if visit_later \
        else _href(visit_later=1)
    # Topic chips keep one topic at a time: clicking the active one clears it,
    # clicking another replaces it — while preserving the active status filter.
    for tc in topic_counts:
        tc["href"] = _href(topic=None) if tc["topic"] == topic \
            else _href(topic=tc["topic"])
    # One-click difficulty chips (Easy/Medium/Hard), same toggle/keep-context rules.
    difficulty_filters = [
        {"name": d, "active": difficulty == d,
         "href": _href(difficulty=None) if difficulty == d else _href(difficulty=d)}
        for d in ("easy", "medium", "hard")
    ]
    # Curated-list chips (e.g. "Blind 73"). One per system collection, with the
    # same toggle/keep-context rules: clicking the active one clears it.
    collection_chips = [
        {"slug": c.slug, "title": c.title, "count": len(c.items),
         "active": c.slug == collection,
         "href": _href(collection=None) if c.slug == collection
                 else _href(collection=c.slug)}
        for c in db.scalars(select(Collection).order_by(Collection.id))
    ]

    # Paginate the (fully filtered) list. `page` is clamped to a valid range so
    # stale/oversized links still render the last page rather than an empty one.
    total = len(problems)
    pages = max(1, math.ceil(total / PROBLEMS_PER_PAGE))
    page = max(1, min(page, pages))
    start = (page - 1) * PROBLEMS_PER_PAGE
    page_problems = problems[start:start + PROBLEMS_PER_PAGE]

    # Current filters as a query string so pagination links keep them.
    base_qs = urlencode({k: v for k, v in (
        ("q", q), ("difficulty", difficulty), ("topic", topic),
        ("collection", collection),
        ("unsolved", 1 if unsolved else None), ("solved", 1 if solved else None),
        ("unknown", 1 if unknown else None), ("known", 1 if known else None),
        ("visit_later", 1 if visit_later else None),
    ) if v})

    return templates.TemplateResponse(request, "index.html", {
        "request": request, "problems": page_problems,
        "solved_ids": solved_ids, "known_ids": known_ids,
        "visit_later_ids": visit_later_ids,
        "user_name": request.state.user_name,
        "f_difficulty": difficulty or "", "f_topic": topic or "", "f_q": q or "",
        "f_collection": collection or "",
        "f_unsolved": bool(unsolved), "f_solved": bool(solved),
        "f_unknown": bool(unknown), "f_visit_later": bool(visit_later),
        "collection_chips": collection_chips,
        "active_collection": active_collection,
        "coll_stats": coll_stats,
        "difficulty_filters": difficulty_filters,
        "unsolved_href": unsolved_href, "unknown_href": unknown_href,
        "visit_later_href": visit_later_href,
        "unsolved_counts": unsolved_counts,
        "topic_counts": topic_counts, "topic_toggle_min": TOPIC_BAR_TOGGLE_MIN,
        "topic_expanded": topic_expanded,
        "page": page, "pages": pages, "total": total, "base_qs": base_qs,
        "page_items": page_window(page, pages),
        "range_start": start + 1 if total else 0,
        "range_end": start + len(page_problems),
    })


@router.get("/random/{difficulty}")
def random_unsolved(difficulty: str, request: Request, db: Session = Depends(get_db)):
    """Redirect to a random published problem of the given difficulty that the
    user hasn't solved *and* hasn't marked "known".

    Backs the quick-pick buttons on the problem list and the "Next problem" button
    after marking one known. If nothing is left, fall back to the filtered list so
    the empty state is clear."""
    if difficulty not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=404, detail="Unknown difficulty")
    skip_ids = (store.user_solved_problem_ids(db, request.state.user_id)
                | store.user_known_problem_ids(db, request.state.user_id))
    candidates = [
        p for p in db.scalars(select(Problem).where(
            Problem.is_published.is_(True), Problem.difficulty == difficulty))
        if p.id not in skip_ids
    ]
    if not candidates:
        return RedirectResponse(f"/?difficulty={difficulty}&unknown=1", status_code=303)
    return RedirectResponse(f"/problems/{random.choice(candidates).slug}", status_code=303)


@router.get("/problems/{slug}")
def problem_detail(slug: str, request: Request, submission: str | None = None,
                   db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    solved = prob.id in store.user_solved_problem_ids(db, request.state.user_id)
    known = prob.id in store.user_known_problem_ids(db, request.state.user_id)
    visit_later = prob.id in store.user_visit_later_problem_ids(
        db, request.state.user_id)
    hidden_count = sum(1 for t in prob.tests if t.hidden)

    # Linked from the progress page ("?submission=<id>"): pre-fill the editor with
    # that past submission's code instead of the starter. Only the owner may load
    # their own submission, and it must belong to this problem; otherwise we fall
    # back to the starter so a stale/forged id can't leak someone else's code.
    initial_code = prob.starter_code
    loaded_submission = None
    if submission:
        sub = db.get(Submission, submission)
        if sub and sub.user_id == request.state.user_id and sub.problem_id == prob.id:
            initial_code = sub.code
            loaded_submission = sub

    # This user's attempts on *this* problem, newest first — backs the
    # "Submissions" tab in the statement panel.
    problem_submissions = list(db.scalars(
        select(Submission).where(
            Submission.user_id == request.state.user_id,
            Submission.problem_id == prob.id,
        ).order_by(Submission.created_at.desc())
    ))

    return templates.TemplateResponse(request, "problem.html", {
        "request": request, "prob": prob, "solved": solved, "known": known,
        "visit_later": visit_later, "tz": _user_tz(request),
        "visible_count": len(prob.tests) - hidden_count, "hidden_count": hidden_count,
        "user_name": request.state.user_name,
        "initial_code": initial_code, "loaded_submission": loaded_submission,
        "problem_submissions": problem_submissions,
        "provided_types": _provided_types(prob),
        # Enables the "Get More Help with AI" button — set by the startup probe.
        "ai_help_enabled": settings.llm_help_available,
    })


@router.get("/me")
def progress_page(request: Request, cal: str | None = None,
                  db: Session = Depends(get_db)):
    uid = request.state.user_id
    subs = list(db.scalars(
        select(Submission).where(Submission.user_id == uid)
        .order_by(Submission.created_at.desc())
    ))
    # Group submissions by problem so each problem shows once (its most recent
    # attempt), with all older attempts collapsed behind an expand toggle. `subs`
    # is newest-first, so dict insertion order keeps groups in recency order and
    # the first item of each group is that problem's latest submission. We then
    # show the most-recently-attempted problems (the limit is per problem, not
    # per attempt, so repeated tries on one problem don't crowd out others).
    grouped: dict[int, list[Submission]] = {}
    for s in subs:
        grouped.setdefault(s.problem_id, []).append(s)
    sub_groups = [
        {"latest": items[0], "older": items[1:], "count": len(items)}
        for items in grouped.values()
    ][:RECENT_PROBLEMS_LIMIT]

    solved_ids = store.user_solved_problem_ids(db, uid)
    known_ids = store.user_known_problem_ids(db, uid)
    solved = list(db.scalars(select(Problem).where(Problem.id.in_(solved_ids)))) \
        if solved_ids else []
    solved_counts = {"easy": 0, "medium": 0, "hard": 0}
    for p in solved:
        if p.difficulty in solved_counts:
            solved_counts[p.difficulty] += 1
    tz = _user_tz(request)
    today = datetime.now(tz).date()
    year, month = progress.parse_cal_month(cal, today)
    units_by_date, blocks_by_date = progress.blocks_by_local_date(
        progress.first_solved(db, uid), tz)
    return templates.TemplateResponse(request, "progress.html", {
        "request": request, "sub_groups": sub_groups, "solved": solved, "tz": tz,
        "solved_counts": solved_counts, "user_name": request.state.user_name,
        "topic_cloud": progress.topic_cloud(solved),
        "unsolved_counts": progress.unsolved_counts(db, solved_ids | known_ids),
        "week_streak": progress.weekly_streak(units_by_date, blocks_by_date, tz),
        "month_cal": progress.month_calendar(blocks_by_date, tz, year, month),
    })


@router.post("/me/name")
def set_name(request: Request, name: str = Form(...), db: Session = Depends(get_db)):
    user = db.get(User, request.state.user_id)
    if user and name.strip():
        user.name = name.strip()[:40]
        db.commit()
    return RedirectResponse("/me", status_code=303)


# --- Optional accounts (V2). See docs/user-accounts-v2.md. -------------------
# Identity stays the cookie-minted guest by default; these routes let a guest
# *optionally* claim an account or log in so progress follows them across
# devices. We keep the V1 raw-id `lc_uid` cookie (bearer) so existing guests
# don't lose progress; signing it is a documented follow-up.
_COOKIE_MAX_AGE = 63_072_000  # ~2 years, matching the guest cookie in main.py


def _set_identity_cookie(resp: RedirectResponse, uid: str) -> None:
    resp.set_cookie("lc_uid", uid, max_age=_COOKIE_MAX_AGE,
                    httponly=True, samesite="lax")


def _account_redirect(error: str) -> RedirectResponse:
    return RedirectResponse(f"/account?error={quote(error)}", status_code=303)


@router.get("/account")
def account(request: Request, error: str | None = None):
    """Sign-up + log-in page for guests; account summary once signed in."""
    return templates.TemplateResponse(request, "account.html", {
        "request": request, "user_name": request.state.user_name,
        "error": error,
    })


@router.post("/account")
def account_create(request: Request, username: str = Form(...),
                   password: str = Form(...), email: str = Form(""),
                   db: Session = Depends(get_db)):
    """Claim the current guest row as an account, keeping all its progress."""
    try:
        user = store.create_account(
            db, request.state.user_id, username, password, email)
    except ValueError as e:
        return _account_redirect(str(e))
    resp = RedirectResponse("/me", status_code=303)
    _set_identity_cookie(resp, user.id)  # same id; refreshes the cookie max-age
    return resp


@router.post("/login")
def login(request: Request, username: str = Form(...), password: str = Form(...),
          db: Session = Depends(get_db)):
    user = store.authenticate(db, username, password)
    if user is None:
        return _account_redirect("Wrong username or password.")
    # Fold any progress made as a guest in this browser into the account
    # (no-op when already this account or already a different account).
    store.merge_user(db, request.state.user_id, user.id)
    resp = RedirectResponse("/me", status_code=303)
    _set_identity_cookie(resp, user.id)
    return resp


@router.post("/logout")
def logout():
    """Drop the identity cookie; the next request mints a fresh guest."""
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("lc_uid")
    return resp
