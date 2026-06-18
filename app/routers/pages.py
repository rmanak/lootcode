"""Server-rendered pages: problem list, problem detail, and per-user progress."""
from __future__ import annotations

import math
import os
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote, urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import store
from ..config import settings
from ..db import get_db
from ..models import Problem, Submission, User
from ..templating import templates

router = APIRouter()


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

# "Units of work" a solve is worth, by difficulty. Each weekday is drawn as a
# 2x8 grid of DAY_BLOCKS little blocks; a solve fills that many grey blocks with
# a difficulty colour (easy 1 light-green, medium 4 yellow, hard 16 red == a full
# day). Anything past a full day spills forward to pre-fill the next day(s).
UNIT_WEIGHTS = {"easy": 1, "medium": 4, "hard": 16}
DAY_BLOCKS = 16  # 2 rows x 8 columns


def _unsolved_counts(db: Session, solved_ids: set[int]) -> dict[str, int]:
    """Count published, still-unsolved problems per difficulty.

    Backs the "jump to a random unsolved" quick-picks on both the problem list
    and the progress page. Always reflects the whole bank, not any active filter."""
    counts = {"easy": 0, "medium": 0, "hard": 0}
    for p in db.scalars(select(Problem).where(Problem.is_published.is_(True))):
        if p.id not in solved_ids and p.difficulty in counts:
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

    Diameter scales with sqrt(count) so a circle's *area* is proportional to the
    count (the honest way to size bubbles). The largest topic fills MAX_PX; the
    rest shrink toward MIN_PX. Each gets a distinct hue the template paints with.
    Sorted by count (then name) so the biggest topics lead."""
    MIN_PX, MAX_PX = 48, 104
    counts: dict[str, int] = {}
    for p in solved:
        for t in (p.topics or []):
            counts[t] = counts.get(t, 0) + 1
    if not counts:
        return []
    top = max(counts.values())
    cloud = []
    for i, (topic, count) in enumerate(
            sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))):
        frac = (count / top) ** 0.5  # 1.0 for the largest topic
        cloud.append({
            "topic": topic, "count": count,
            "size": round(MIN_PX + frac * (MAX_PX - MIN_PX)),
            "hue": (i * 67) % 360,  # spread hues around the wheel
        })
    return cloud


def _user_tz(request: Request) -> ZoneInfo:
    """The visitor's timezone, from the client-set `lc_tz` cookie (falling back
    to UTC). The weekly grid buckets solves by the user's *local* day, so a
    late-night solve fills tonight's column instead of rolling into tomorrow's."""
    name = request.cookies.get("lc_tz")
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError):
            pass
    return ZoneInfo("UTC")


def _weekly_streak(db: Session, user_id: str, tz: ZoneInfo) -> dict:
    """Per-weekday (Mon–Fri) block grid of work completed this week.

    A problem counts once, on the day it was *first* solved, and is worth
    `UNIT_WEIGHTS` blocks (easy 1, medium 4, hard 16). Each day's grid holds
    `DAY_BLOCKS` blocks; blocks beyond a full day spill forward to pre-fill the
    next day(s). Solve times are stored as UTC and bucketed by the user's local
    day (`tz`), so an evening solve lands on the day it felt like, not the next."""
    # Earliest solving submission per problem (rows already time-ordered).
    first_solved: dict[int, Submission] = {}
    for s in db.scalars(
        select(Submission).where(
            Submission.user_id == user_id,
            Submission.total_count > 0,
            Submission.passed_count == Submission.total_count,
        ).order_by(Submission.created_at)
    ):
        first_solved.setdefault(s.problem_id, s)

    today = datetime.now(tz).date()
    monday = today - timedelta(days=today.weekday())  # Monday == weekday 0
    week_days = [monday + timedelta(days=i) for i in range(5)]  # Mon … Fri

    # Per day: the units earned that day, and a flat list of coloured blocks (one
    # difficulty tag per unit of work), in solve order.
    units_by_date = {d: 0 for d in week_days}
    blocks_by_date: dict[object, list[str]] = {d: [] for d in week_days}
    for s in first_solved.values():  # iterated in created_at order
        # created_at is naive UTC; reinterpret in the user's zone for bucketing.
        d = s.created_at.replace(tzinfo=timezone.utc).astimezone(tz).date()
        if d in units_by_date:
            diff = s.problem.difficulty if s.problem.difficulty in UNIT_WEIGHTS else "easy"
            weight = UNIT_WEIGHTS[diff]
            units_by_date[d] += weight
            blocks_by_date[d].extend(diff for _ in range(weight))

    # Lay each day's blocks into its DAY_BLOCKS-slot grid; whatever overflows a
    # full day is carried forward to pre-fill the following day(s).
    days = []
    carry: list[str] = []
    for d in week_days:
        filled = carry + blocks_by_date[d]
        placed, carry = filled[:DAY_BLOCKS], filled[DAY_BLOCKS:]
        # "" renders as a grey (empty) block; a difficulty name colours it.
        cells = [placed[i] if i < len(placed) else "" for i in range(DAY_BLOCKS)]
        days.append({
            "label": d.strftime("%a"),
            "units": units_by_date[d],
            "filled": len(placed),
            "cells": cells,
            "met": len(placed) >= DAY_BLOCKS,
            "is_today": d == today,
            "is_future": d > today,
        })

    return {
        "days": days,
        "goal": DAY_BLOCKS,
        "total": sum(units_by_date.values()),
        # A still-to-come day pre-filled by overflow isn't a day you "hit".
        "days_met": sum(1 for x in days if x["met"] and not x["is_future"]),
    }


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
          q: str | None = None, unsolved: int = 0, solved: int = 0, page: int = 1,
          db: Session = Depends(get_db)):
    stmt = select(Problem).where(Problem.is_published.is_(True))
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    if q:
        stmt = stmt.where(Problem.title.ilike(f"%{q}%"))
    problems = list(db.scalars(stmt.order_by(Problem.id)))
    if topic:
        problems = [p for p in problems if topic in (p.topics or [])]

    solved_ids = store.user_solved_problem_ids(db, request.state.user_id)
    if unsolved:
        problems = [p for p in problems if p.id not in solved_ids]
    # "See all" from the My Progress summary links here with solved=1.
    if solved:
        problems = [p for p in problems if p.id in solved_ids]

    all_topics = sorted({t for p in db.scalars(select(Problem)) for t in (p.topics or [])})

    # Category bar: published-problem count per topic, most-common first. If the
    # active topic filter is one of the "extra" (hidden) chips, start expanded so
    # the highlighted chip is visible.
    topic_counts = _topic_counts(db)
    topic_expanded = bool(topic) and any(
        tc["topic"] == topic for tc in topic_counts[TOPIC_BAR_TOP_N:])

    # Unsolved counts per difficulty, for the "jump to a random unsolved" buttons.
    unsolved_counts = _unsolved_counts(db, solved_ids)

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
        ("unsolved", 1 if unsolved else None), ("solved", 1 if solved else None),
    ) if v})

    return templates.TemplateResponse(request, "index.html", {
        "request": request, "problems": page_problems, "all_topics": all_topics,
        "solved_ids": solved_ids, "user_name": request.state.user_name,
        "f_difficulty": difficulty or "", "f_topic": topic or "", "f_q": q or "",
        "f_unsolved": bool(unsolved), "f_solved": bool(solved),
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
    """Redirect to a random unsolved, published problem of the given difficulty.

    Backs the quick-pick buttons on the problem list. If the user has cleared
    that difficulty, fall back to the filtered list so the empty state is clear."""
    if difficulty not in ("easy", "medium", "hard"):
        raise HTTPException(status_code=404, detail="Unknown difficulty")
    solved_ids = store.user_solved_problem_ids(db, request.state.user_id)
    candidates = [
        p for p in db.scalars(select(Problem).where(
            Problem.is_published.is_(True), Problem.difficulty == difficulty))
        if p.id not in solved_ids
    ]
    if not candidates:
        return RedirectResponse(f"/?difficulty={difficulty}&unsolved=1", status_code=303)
    return RedirectResponse(f"/problems/{random.choice(candidates).slug}", status_code=303)


@router.get("/problems/{slug}")
def problem_detail(slug: str, request: Request, submission: str | None = None,
                   db: Session = Depends(get_db)):
    prob = db.scalar(select(Problem).where(Problem.slug == slug))
    if prob is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    solved = prob.id in store.user_solved_problem_ids(db, request.state.user_id)
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
        "request": request, "prob": prob, "solved": solved,
        "visible_count": len(prob.tests) - hidden_count, "hidden_count": hidden_count,
        "user_name": request.state.user_name,
        "initial_code": initial_code, "loaded_submission": loaded_submission,
    })


@router.get("/me")
def progress(request: Request, db: Session = Depends(get_db)):
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
    solved = list(db.scalars(select(Problem).where(Problem.id.in_(solved_ids)))) \
        if solved_ids else []
    solved_counts = {"easy": 0, "medium": 0, "hard": 0}
    for p in solved:
        if p.difficulty in solved_counts:
            solved_counts[p.difficulty] += 1
    return templates.TemplateResponse(request, "progress.html", {
        "request": request, "sub_groups": sub_groups, "solved": solved,
        "solved_counts": solved_counts, "user_name": request.state.user_name,
        "topic_cloud": _topic_cloud(solved),
        "unsolved_counts": _unsolved_counts(db, solved_ids),
        "week_streak": _weekly_streak(db, uid, _user_tz(request)),
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
