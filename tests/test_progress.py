"""Direct tests for `app/progress.py`.

These rules used to live inline in the `/me` route handler, so the only way to
exercise them was to render the page and read the HTML back — which is why the
weekly grid and the month calendar were able to disagree about whether a day was
complete (see ``test_calendar_green_matches_weekly_met_with_spillover``). Now
they are plain functions and can be checked at the boundary that actually
matters: the layout rules, the timezone bucketing, and the sizing curve.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pytest

from app.progress import (
    DAY_BLOCKS,
    UNIT_WEIGHTS,
    blocks_by_local_date,
    lay_out_week,
    month_calendar,
    parse_cal_month,
    topic_cloud,
    topic_counts,
    unsolved_counts,
    weekly_streak,
)

UTC = ZoneInfo("UTC")
WEEK = [date(2026, 6, 21 + i) for i in range(7)]  # Sun 21 June … Sat 27 June


# --- lay_out_week ----------------------------------------------------------

def test_lay_out_week_spills_overflow_forward():
    # Two full days of work on Sunday fills Sunday and pre-fills Monday.
    placed = lay_out_week(WEEK, {WEEK[0]: ["easy"] * (DAY_BLOCKS * 2)})
    assert len(placed[0]) == DAY_BLOCKS
    assert len(placed[1]) == DAY_BLOCKS
    assert placed[2] == []


def test_lay_out_week_carry_does_not_cross_weeks():
    # Carry starts empty every Sunday, so a week's completion never depends on a
    # different week — the property the month calendar relies on to agree with
    # the weekly grid.
    huge = {WEEK[6]: ["hard"] * (DAY_BLOCKS * 3)}   # Saturday, wildly over
    assert len(lay_out_week(WEEK, huge)[6]) == DAY_BLOCKS
    next_week = [date(2026, 6, 28) + timedelta(days=i) for i in range(7)]
    assert lay_out_week(next_week, huge) == [[] for _ in range(7)]


def test_lay_out_week_preserves_difficulty_order():
    blocks = {WEEK[0]: ["easy", "medium", "hard"]}
    assert lay_out_week(WEEK, blocks)[0] == ["easy", "medium", "hard"]


# --- weekly_streak ---------------------------------------------------------

def test_weekly_streak_future_day_prefilled_by_overflow_is_not_met(monkeypatch):
    """A still-to-come day that overflow already filled is not a day you *hit*."""
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 21, 12, tzinfo=tz)  # Sunday

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    blocks = {WEEK[0]: ["hard"] * (DAY_BLOCKS * 3)}  # Sun spills into Mon and Tue
    units = {WEEK[0]: DAY_BLOCKS * 3}
    ws = weekly_streak(units, blocks, UTC)

    assert [d["met"] for d in ws["days"][:3]] == [True, True, True]
    assert [d["is_future"] for d in ws["days"][:3]] == [False, True, True]
    assert ws["days_met"] == 1          # only Sunday actually happened
    assert ws["goal"] == DAY_BLOCKS
    assert ws["total"] == DAY_BLOCKS * 3
    assert [d["label"] for d in ws["days"]] == [
        "Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    assert all(len(d["cells"]) == DAY_BLOCKS for d in ws["days"])


# --- month_calendar --------------------------------------------------------

def test_month_calendar_never_pages_into_the_future(monkeypatch):
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 15, 12, tzinfo=tz)

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    assert month_calendar({}, UTC, 2026, 6)["has_next"] is False   # current month
    assert month_calendar({}, UTC, 2026, 5)["has_next"] is True    # a past month
    # Year boundaries roll rather than producing month 0 / month 13.
    assert month_calendar({}, UTC, 2026, 1)["prev"] == "2025-12"
    assert month_calendar({}, UTC, 2025, 12)["next"] == "2026-01"


def test_month_calendar_adjacent_month_cells_are_blank_but_still_spill(monkeypatch):
    """A trailing day of the previous month can complete an in-month day."""
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 7, 31, 12, tzinfo=tz)

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    # 28 June (Sun) is in the same Sun–Sat week as 1 July (Wed). Dump four days
    # of work on it: it spills through 29, 30 June and fills 1 July.
    blocks = {date(2026, 6, 28): ["hard"] * (DAY_BLOCKS * 4)}
    # Index positionally: the day *number* is ambiguous across the two months the
    # grid shows (there is a 28 June and a 28 July in it).
    first_week = month_calendar(blocks, UTC, 2026, 7)["weeks"][0]
    june_28, july_1 = first_week[0], first_week[3]
    assert (june_28["day"], june_28["in_month"], june_28["done"]) == (28, False, False)
    assert (july_1["day"], july_1["in_month"], july_1["done"]) == (1, True, True)


# --- parse_cal_month -------------------------------------------------------

@pytest.mark.parametrize("value", [None, "", "nonsense", "2026", "2026-13",
                                   "2026-00", "abcd-ef", "2026-06-01x"])
def test_parse_cal_month_falls_back_to_today(value):
    today = date(2026, 6, 15)
    assert parse_cal_month(value, today) == (2026, 6)


def test_parse_cal_month_accepts_the_past_and_clamps_the_future():
    today = date(2026, 6, 15)
    assert parse_cal_month("2025-01", today) == (2025, 1)
    assert parse_cal_month("2026-06", today) == (2026, 6)   # the current month
    assert parse_cal_month("2026-07", today) == (2026, 6)   # next month clamps
    assert parse_cal_month("2099-01", today) == (2026, 6)


# --- blocks_by_local_date --------------------------------------------------

def _solve(problem_id: int, when: datetime, difficulty: str):
    return SimpleNamespace(problem_id=problem_id, created_at=when,
                           problem=SimpleNamespace(difficulty=difficulty))


def test_blocks_by_local_date_buckets_on_the_users_day():
    """23:00 in New York on the 20th is 03:00 UTC on the 21st. The solve belongs
    to the day it felt like, which is what the cookie timezone is for."""
    solves = {1: _solve(1, datetime(2026, 6, 21, 3, 0), "easy")}  # stored UTC
    ny = ZoneInfo("America/New_York")
    units_ny, blocks_ny = blocks_by_local_date(solves, ny)
    units_utc, _ = blocks_by_local_date(solves, UTC)
    assert list(units_ny) == [date(2026, 6, 20)]
    assert list(units_utc) == [date(2026, 6, 21)]
    assert blocks_ny[date(2026, 6, 20)] == ["easy"]


def test_blocks_by_local_date_weights_by_difficulty():
    solves = {
        1: _solve(1, datetime(2026, 6, 21, 12), "easy"),
        2: _solve(2, datetime(2026, 6, 21, 13), "medium"),
        3: _solve(3, datetime(2026, 6, 21, 14), "hard"),
    }
    units, blocks = blocks_by_local_date(solves, UTC)
    day = date(2026, 6, 21)
    assert units[day] == sum(UNIT_WEIGHTS.values())
    assert blocks[day].count("hard") == UNIT_WEIGHTS["hard"]
    assert blocks[day].count("medium") == UNIT_WEIGHTS["medium"]


def test_blocks_by_local_date_treats_an_unknown_difficulty_as_easy():
    solves = {1: _solve(1, datetime(2026, 6, 21, 12), "impossible")}
    units, blocks = blocks_by_local_date(solves, UTC)
    assert units[date(2026, 6, 21)] == UNIT_WEIGHTS["easy"]
    assert blocks[date(2026, 6, 21)] == ["easy"]


# --- topic_cloud -----------------------------------------------------------

def test_topic_cloud_is_empty_without_solves():
    assert topic_cloud([]) == []
    assert topic_cloud([SimpleNamespace(topics=None)]) == []


def test_topic_cloud_sizes_by_log2_and_orders_by_count():
    solved = ([SimpleNamespace(topics=["arrays"])] * 3
              + [SimpleNamespace(topics=["graphs", "arrays"])])
    cloud = topic_cloud(solved)
    assert [c["topic"] for c in cloud] == ["arrays", "graphs"]
    assert [c["count"] for c in cloud] == [4, 1]
    # One solve is the base unit; doubling adds roughly one more unit of diameter.
    one = topic_cloud([SimpleNamespace(topics=["x"])])[0]["size"]
    two = topic_cloud([SimpleNamespace(topics=["x"])] * 3)[0]["size"]
    assert two == pytest.approx(one * 2, abs=1)
    assert all(0 <= c["hue"] < 360 for c in cloud)


def test_topic_cloud_breaks_count_ties_by_name():
    solved = [SimpleNamespace(topics=["zebra", "apple"])]
    assert [c["topic"] for c in topic_cloud(solved)] == ["apple", "zebra"]


# --- the two DB-backed counters -------------------------------------------

def test_unsolved_counts_skips_what_it_is_given(client, db):
    from sqlalchemy import select

    from app.models import Problem

    full = unsolved_counts(db, set())
    assert sum(full.values()) > 0
    assert set(full) == {"easy", "medium", "hard"}

    easy_id = db.scalar(
        select(Problem.id).where(Problem.is_published.is_(True),
                                 Problem.difficulty == "easy"))
    skipped = unsolved_counts(db, {easy_id})
    assert skipped["easy"] == full["easy"] - 1
    assert skipped["medium"] == full["medium"]


def test_topic_counts_is_sorted_most_common_first(client, db):
    counts = topic_counts(db)
    assert counts, "the seeded bank has topics"
    keys = [(-c["count"], c["topic"]) for c in counts]
    assert keys == sorted(keys)
    assert all(c["count"] > 0 for c in counts)
