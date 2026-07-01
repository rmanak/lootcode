"""Server-rendered pages: problem list, problem detail, and per-user progress."""
from __future__ import annotations

import calendar
import math
import os
import random
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, unquote, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import store
from ..config import settings
from ..db import get_db
from ..models import Collection, Problem, Submission, User
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
}


def _provided_types(prob) -> dict:
    """Map of declared custom type -> its definition snippet, for types this
    problem actually uses as a param or return."""
    used = {(p.get("type") or "") for p in (prob.params or [])}
    used.add(prob.return_type or "")
    return {t: PROVIDED_TYPE_DEFS[t] for t in used if t in PROVIDED_TYPE_DEFS}


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

# How many topic chips the category bar shows before the "Expand" toggle.
TOPIC_BAR_TOP_N = 8

# How many problems the "Recent submissions" list shows. The cap is per problem
# (each shown with its full attempt history), not per attempt.
RECENT_PROBLEMS_LIMIT = 25

# "Units of work" a solve is worth, by difficulty. Each weekday is drawn as an
# 10x2 grid of DAY_BLOCKS little blocks; a solve fills that many grey blocks with
# a difficulty colour (easy 1 light-green, medium 4 yellow, hard 10 red). Anything
# past a full day spills forward to pre-fill the next day(s).
UNIT_WEIGHTS = {"easy": 1, "medium": 4, "hard": 10}
DAY_BLOCKS = 20  # 10 rows x 2 columns


def _unsolved_counts(db: Session, skip_ids: set[int]) -> dict[str, int]:
    """Count published problems per difficulty that are still worth surfacing —
    i.e. neither solved nor marked "known" (pass `skip_ids = solved | known`).

    Backs the "jump to a random unsolved" quick-picks on both the problem list
    and the progress page, so the per-difficulty counts match the pool the random
    jump draws from. Always reflects the whole bank, not any active filter."""
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for p in db.scalars(select(Problem).where(Problem.is_published.is_(True))):
        if p.id not in skip_ids and p.difficulty in counts:
            counts[p.difficulty] += 1
    return counts


def _topic_counts(db: Session) -> list[dict]:
    """Published-problem count per topic tag, most-common first (ties by name).

    Backs the collapsible category bar above the problem list; each entry is a
    chip that filters the list to that topic. Counts the whole published bank
    (independent of any active filter), so the numbers match what clicking a
    chip lands you on."""
    counts: dict[str, int] = {}
    for p in db.scalars(select(Problem).where(Problem.is_published.is_(True))):
        for t in (p.topics or []):
            counts[t] = counts.get(t, 0) + 1
    return [{"topic": t, "count": c}
            for t, c in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))]


def _topic_cloud(solved: list[Problem]) -> list[dict]:
    """Bubble-cloud data for the My Progress summary: one circle per topic the
    user has solved at least one problem in, sized by how many.

    Diameter scales with log2(1 + count): a single solved problem is the base
    unit (log2(2) = 1), and past that *doubling* the count adds roughly one unit
    of diameter (a 32-solve topic is ~1 unit bigger than a 16-solve one). This is
    deliberately gentle, so heavily-solved topics don't dwarf the rest. Small
    topics can end up too small to read comfortably — that's fine; the cloud's
    zoom button blows everything up for a closer look. Each gets a distinct hue
    the template paints with. Sorted by count (then name) so the biggest lead."""
    UNIT_PX = 26  # pixels per log2 unit; count == 1 -> one unit -> 26px bubble
    counts: dict[str, int] = {}
    for p in solved:
        for t in (p.topics or []):
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return []
    cloud = []
    for i, (topic, count) in enumerate(
            sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))):
        units = math.log2(1 + count)  # 1.0 for a single solved problem
        cloud.append({
            "topic": topic, "count": count,
            "size": round(UNIT_PX * units),
            "hue": (i * 67) % 360,  # spread hues around the wheel
        })
    return cloud


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


def _first_solved(db: Session, user_id: str) -> dict[int, Submission]:
    """Earliest *solving* submission per problem (one entry per solved problem).

    Rows arrive in `created_at` order, so the first time we see a problem id is
    the moment it was first solved; later attempts don't re-count it."""
    first_solved: dict[int, Submission] = {}
    for s in db.scalars(
        select(Submission).where(
            Submission.user_id == user_id,
            Submission.total_count > 0,
            Submission.passed_count == Submission.total_count,
        ).order_by(Submission.created_at)
    ):
        first_solved.setdefault(s.problem_id, s)
    return first_solved


def _blocks_by_local_date(
    first_solved: dict[int, Submission], tz: ZoneInfo
) -> tuple[dict[date, int], dict[date, list[str]]]:
    """Bucket each first-solve onto its *local* day, returning per-day units and a
    flat list of coloured blocks (one difficulty tag per unit of work).

    A solve is worth `UNIT_WEIGHTS` blocks (easy 1, medium 4, hard 10). Solve
    times are stored as UTC and bucketed by the user's local day (`tz`), so an
    evening solve lands on the day it felt like, not the next."""
    units_by_date: dict[date, int] = {}
    blocks_by_date: dict[date, list[str]] = {}
    for s in first_solved.values():  # iterated in created_at order
        d = s.created_at.replace(tzinfo=timezone.utc).astimezone(tz).date()
        diff = s.problem.difficulty if s.problem.difficulty in UNIT_WEIGHTS else "easy"
        weight = UNIT_WEIGHTS[diff]
        units_by_date[d] = units_by_date.get(d, 0) + weight
        blocks_by_date.setdefault(d, []).extend(diff for _ in range(weight))
    return units_by_date, blocks_by_date


def _lay_out_week(
    week_days: list[date], blocks_by_date: dict[date, list[str]]
) -> list[list[str]]:
    """Place each day's difficulty-blocks into its `DAY_BLOCKS`-slot grid, carrying
    whatever overflows a full day forward to pre-fill later days *in the same week*.

    Returns one placed-block list per day, aligned with `week_days` (assumed to be
    seven consecutive Sun–Sat dates). Carry starts empty at the week's Sunday, so a
    week's completion never depends on a different week — this is the single source
    of truth for "did a day hit the goal", shared by the weekly grid and the month
    calendar so the two views can't disagree about a day."""
    placed_per_day: list[list[str]] = []
    carry: list[str] = []
    for d in week_days:
        filled = carry + blocks_by_date.get(d, [])
        placed, carry = filled[:DAY_BLOCKS], filled[DAY_BLOCKS:]
        placed_per_day.append(placed)
    return placed_per_day


def _weekly_streak(
    units_by_date: dict[date, int], blocks_by_date: dict[date, list[str]], tz: ZoneInfo
) -> dict:
    """Per-weekday (Sun–Sat, weekend included) block grid for the current week.

    Each day's grid holds `DAY_BLOCKS` blocks; blocks beyond a full day spill
    forward to pre-fill the next day(s)."""
    today = datetime.now(tz).date()
    # Sunday that starts this week. weekday(): Mon=0 … Sun=6, so (weekday+1)%7 is
    # the number of days back to the most recent Sunday.
    sunday = today - timedelta(days=(today.weekday() + 1) % 7)
    week_days = [sunday + timedelta(days=i) for i in range(7)]  # Sun … Sat

    days = []
    for d, placed in zip(week_days, _lay_out_week(week_days, blocks_by_date)):
        # "" renders as a grey (empty) block; a difficulty name colours it.
        cells = [placed[i] if i < len(placed) else "" for i in range(DAY_BLOCKS)]
        days.append({
            "label": d.strftime("%a"),
            "units": units_by_date.get(d, 0),
            "filled": len(placed),
            "cells": cells,
            "met": len(placed) >= DAY_BLOCKS,
            "is_today": d == today,
            "is_future": d > today,
        })

    return {
        "days": days,
        "goal": DAY_BLOCKS,
        "total": sum(units_by_date.get(d, 0) for d in week_days),
        # A still-to-come day pre-filled by overflow isn't a day you "hit".
        "days_met": sum(1 for x in days if x["met"] and not x["is_future"]),
    }


def _month_calendar(
    blocks_by_date: dict[date, list[str]], tz: ZoneInfo, year: int, month: int
) -> dict:
    """A month grid (Sunday-first) marking which days hit the daily `DAY_BLOCKS` goal.

    A day is `done` when its blocks — including overflow spilled forward from
    earlier in the *same* Sun–Sat week — fill the day, exactly as the weekly grid
    counts it (both go through `_lay_out_week`), so a day shown ✓ for this week also
    lights up green here. Still-to-come days never light up (you can't have hit a
    day that hasn't happened). Cells from adjacent months render blank (`in_month`
    False) but still contribute their spillover to in-month days in the same week."""
    today = datetime.now(tz).date()
    cal = calendar.Calendar(firstweekday=6)  # 6 == Sunday

    weeks = [
        [
            {
                "day": d.day,
                "in_month": d.month == month,
                "done": (
                    d.month == month and d <= today and len(placed) >= DAY_BLOCKS
                ),
                "is_today": d == today,
                "is_future": d > today,
            }
            for d, placed in zip(week, _lay_out_week(week, blocks_by_date))
        ]
        for week in cal.monthdatescalendar(year, month)
    ]

    prev_y, prev_m = (year - 1, 12) if month == 1 else (year, month - 1)
    next_y, next_m = (year + 1, 1) if month == 12 else (year, month + 1)
    return {
        "label": date(year, month, 1).strftime("%B %Y"),
        "weekday_labels": ["S", "M", "T", "W", "T", "F", "S"],
        "weeks": weeks,
        "prev": f"{prev_y:04d}-{prev_m:02d}",
        "next": f"{next_y:04d}-{next_m:02d}",
        # Don't let users page forward into empty future months.
        "has_next": (year, month) < (today.year, today.month),
    }


def _parse_cal_month(cal: str | None, today: date) -> tuple[int, int]:
    """Parse a `YYYY-MM` calendar param into (year, month), clamped to a real
    month and never past the current one; falls back to today's month."""
    if cal:
        try:
            y, m = cal.split("-", 1)
            year, month = int(y), int(m)
            date(year, month, 1)  # validate month range
            if (year, month) <= (today.year, today.month):
                return year, month
        except (ValueError, TypeError):
            pass
    return today.year, today.month


def _page_window(page: int, pages: int, span: int = 2) -> list[int | None]:
    """Page numbers to show, with `None` marking an ellipsis gap.

    Always includes the first/last page and a small window around `page`,
    e.g. [1, None, 4, 5, 6, None, 20]."""
    if pages <= 7:
        return list(range(1, pages + 1))
    wanted = {1, pages, page}
    for d in range(1, span + 1):
        wanted.add(page - d)
        wanted.add(page + d)
    items: list[int | None] = []
    prev = 0
    for n in sorted(n for n in wanted if 1 <= n <= pages):
        if n - prev > 1:
            items.append(None)
        items.append(n)
        prev = n
    return items

# Figures live at content/problems/<slug>/assets/<file> (see docs/problem-images.md).
# Only these image types are served; never the problem's solution/ or tests/.
_IMAGE_MEDIA = {
    ".svg": "image/svg+xml", ".png": "image/png", ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp",
}


@router.get("/problems/{slug}/assets/{filename}")
def problem_asset(slug: str, filename: str):
    """Serve a problem figure. Deliberately narrow: only the per-problem `assets/`
    dir, only image extensions, and path-traversal is rejected."""
    if any(bad in slug for bad in ("/", "\\", "..")) or \
       any(bad in filename for bad in ("/", "\\", "..")):
        raise HTTPException(status_code=404, detail="Not found")
    media_type = _IMAGE_MEDIA.get(Path(filename).suffix.lower())
    if media_type is None:
        raise HTTPException(status_code=404, detail="Not found")

    assets_dir = (settings.CONTENT_DIR / slug / "assets").resolve()
    target = (assets_dir / filename).resolve()
    # Belt-and-suspenders: the resolved file must stay inside that assets dir.
    if os.path.commonpath([str(assets_dir), str(target)]) != str(assets_dir) \
       or not target.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(target, media_type=media_type)


@router.get("/")
def index(request: Request, difficulty: str | None = None, topic: str | None = None,
          q: str | None = None, collection: str | None = None, unsolved: int = 0,
          solved: int = 0, unknown: int = 0, visit_later: int = 0, page: int = 1,
          db: Session = Depends(get_db)):
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
    # "Visit later" is an independent bookmark axis — it shows only flagged
    # problems and combines freely with every other filter (incl. the status
    # chips above), so it isn't part of their mutually-exclusive group.
    if visit_later:
        problems = [p for p in problems if p.id in visit_later_ids]

    # When a curated list is active, present it in its study order (position)
    # rather than by problem id.
    if active_collection:
        problems.sort(key=lambda p: coll_order[p.id])

    # Category bar: published-problem count per topic, most-common first. If the
    # active topic filter is one of the "extra" (hidden) chips, start expanded so
    # the highlighted chip is visible.
    topic_counts = _topic_counts(db)
    topic_expanded = bool(topic) and any(
        tc["topic"] == topic for tc in topic_counts[TOPIC_BAR_TOP_N:])

    # Counts per difficulty for the "jump to a random unsolved" buttons — skipping
    # solved *and* known so the count matches what the random jump can land on.
    unsolved_counts = _unsolved_counts(db, solved_ids | known_ids)

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
        ("unknown", 1 if unknown else None),
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
        "difficulty_filters": difficulty_filters,
        "unsolved_href": unsolved_href, "unknown_href": unknown_href,
        "visit_later_href": visit_later_href,
        "unsolved_counts": unsolved_counts,
        "topic_counts": topic_counts, "topic_top_n": TOPIC_BAR_TOP_N,
        "topic_expanded": topic_expanded,
        "page": page, "pages": pages, "total": total, "base_qs": base_qs,
        "page_items": _page_window(page, pages),
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

    return templates.TemplateResponse(request, "problem.html", {
        "request": request, "prob": prob, "solved": solved, "known": known,
        "visit_later": visit_later, "tz": _user_tz(request),
        "visible_count": len(prob.tests) - hidden_count, "hidden_count": hidden_count,
        "user_name": request.state.user_name,
        "initial_code": initial_code, "loaded_submission": loaded_submission,
        "provided_types": _provided_types(prob),
    })


@router.get("/me")
def progress(request: Request, cal: str | None = None, db: Session = Depends(get_db)):
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
    year, month = _parse_cal_month(cal, today)
    units_by_date, blocks_by_date = _blocks_by_local_date(_first_solved(db, uid), tz)
    return templates.TemplateResponse(request, "progress.html", {
        "request": request, "sub_groups": sub_groups, "solved": solved, "tz": tz,
        "solved_counts": solved_counts, "user_name": request.state.user_name,
        "topic_cloud": _topic_cloud(solved),
        "unsolved_counts": _unsolved_counts(db, solved_ids | known_ids),
        "week_streak": _weekly_streak(units_by_date, blocks_by_date, tz),
        "month_cal": _month_calendar(blocks_by_date, tz, year, month),
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
