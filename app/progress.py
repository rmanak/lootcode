"""Progress, streak and topic statistics for the My Progress page.

Everything here is a pure function of its arguments (a `Session`, a list of
`Problem`/`Submission` rows, a timezone) — no `Request`, no template, no
response. It lived inline in `routers/pages.py`, where the weekly-grid and
month-calendar layout rules could only be exercised by rendering a page; the
block-spill logic in particular (`lay_out_week`) is the single source of truth
for "did a day hit the goal" and is shared by two different views, so it is
worth being able to test directly.

The timezone comes in as a parameter: solves are stored in UTC and bucketed by
the *user's* local day, so an evening solve fills tonight's column rather than
rolling into tomorrow's. Reading that timezone off the request cookie stays in
the router, where the request is.
"""
from __future__ import annotations

import calendar
import math
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Problem, Submission

# "Units of work" a solve is worth, by difficulty. Each weekday is drawn as an
# 8x2 grid of DAY_BLOCKS little blocks; a solve fills that many grey blocks with
# a difficulty colour (easy 1 light-green, medium 4 yellow, hard 8 red). Anything
# past a full day spills forward to pre-fill the next day(s).
UNIT_WEIGHTS = {"easy": 1, "medium": 4, "hard": 8}
DAY_BLOCKS = 16  # 8 rows x 2 columns


def unsolved_counts(db: Session, skip_ids: set[int]) -> dict[str, int]:
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


def topic_counts(db: Session) -> list[dict]:
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


def topic_cloud(solved: list[Problem]) -> list[dict]:
    """Bubble-cloud data for the My Progress summary: one circle per topic the
    user has solved at least one problem in, sized by how many.

    Diameter scales with log2(1 + count): a single solved problem is the base
    unit (log2(2) = 1), and past that *doubling* the count adds roughly one unit
    of diameter (a 32-solve topic is ~1 unit bigger than a 16-solve one). This is
    deliberately gentle, so heavily-solved topics don't dwarf the rest. Small
    topics can end up too small to read comfortably — that's fine; the cloud's
    zoom button blows everything up for a closer look. Each gets a distinct hue
    the template paints with. Sorted by count (then name) so the biggest lead."""
    UNIT_PX = 26  # noqa: N806 - a constant, scoped to this function; pixels per log2 unit; count == 1 -> one unit -> 26px bubble
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


def first_solved(db: Session, user_id: str) -> dict[int, Submission]:
    """Earliest *solving* submission per problem (one entry per solved problem).

    Rows arrive in `created_at` order, so the first time we see a problem id is
    the moment it was first solved; later attempts don't re-count it."""
    earliest: dict[int, Submission] = {}
    for s in db.scalars(
        select(Submission).where(
            Submission.user_id == user_id,
            Submission.total_count > 0,
            Submission.passed_count == Submission.total_count,
        ).order_by(Submission.created_at)
    ):
        earliest.setdefault(s.problem_id, s)
    return earliest


def blocks_by_local_date(
    solves: dict[int, Submission], tz: ZoneInfo
) -> tuple[dict[date, int], dict[date, list[str]]]:
    """Bucket each first-solve onto its *local* day, returning per-day units and a
    flat list of coloured blocks (one difficulty tag per unit of work).

    A solve is worth `UNIT_WEIGHTS` blocks (easy 1, medium 4, hard 8). Solve
    times are stored as UTC and bucketed by the user's local day (`tz`), so an
    evening solve lands on the day it felt like, not the next."""
    units_by_date: dict[date, int] = {}
    by_date: dict[date, list[str]] = {}
    for s in solves.values():  # iterated in created_at order
        d = s.created_at.replace(tzinfo=UTC).astimezone(tz).date()
        diff = s.problem.difficulty if s.problem.difficulty in UNIT_WEIGHTS else "easy"
        weight = UNIT_WEIGHTS[diff]
        units_by_date[d] = units_by_date.get(d, 0) + weight
        by_date.setdefault(d, []).extend(diff for _ in range(weight))
    return units_by_date, by_date


def lay_out_week(
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


def weekly_streak(
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
    for d, placed in zip(week_days, lay_out_week(week_days, blocks_by_date)):
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


def month_calendar(
    blocks_by_date: dict[date, list[str]], tz: ZoneInfo, year: int, month: int
) -> dict:
    """A month grid (Sunday-first) marking which days hit the daily `DAY_BLOCKS` goal.

    A day is `done` when its blocks — including overflow spilled forward from
    earlier in the *same* Sun–Sat week — fill the day, exactly as the weekly grid
    counts it (both go through `lay_out_week`), so a day shown ✓ for this week also
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
            for d, placed in zip(week, lay_out_week(week, blocks_by_date))
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


def parse_cal_month(cal: str | None, today: date) -> tuple[int, int]:
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
