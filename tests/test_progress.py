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
    carry_into,
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


def test_lay_out_week_carry_crosses_into_next_week():
    # Overflow past Saturday isn't dropped: it pre-fills the following week.
    huge = {WEEK[6]: ["hard"] * (DAY_BLOCKS * 3)}   # Saturday, wildly over
    assert len(lay_out_week(WEEK, huge)[6]) == DAY_BLOCKS
    next_week = [date(2026, 6, 28) + timedelta(days=i) for i in range(7)]
    assert [len(p) for p in lay_out_week(next_week, huge)] == [
        DAY_BLOCKS, DAY_BLOCKS, 0, 0, 0, 0, 0]


def test_lay_out_week_partial_carry_lands_on_next_sunday():
    # Friday 1.5 days over (carry in from Thursday + its own) fills Fri and Sat
    # and leaves the rest for Sunday, ahead of Sunday's own solves.
    blocks = {WEEK[5]: ["medium"] * (DAY_BLOCKS * 2 + 3),
              date(2026, 6, 28): ["easy"]}
    next_week = [date(2026, 6, 28) + timedelta(days=i) for i in range(7)]
    assert lay_out_week(next_week, blocks)[0] == ["medium"] * 3 + ["easy"]


def test_carry_drains_one_day_per_day_across_quiet_stretches():
    # Four days' worth on 1 June: it fills 1–4 June and is gone by the 5th, even
    # though nothing was solved in between, and is still gone weeks later.
    blocks = {date(2026, 6, 1): ["hard"] * (DAY_BLOCKS * 4)}
    assert len(carry_into(date(2026, 6, 4), blocks)) == DAY_BLOCKS
    assert carry_into(date(2026, 6, 5), blocks) == []
    assert lay_out_week(WEEK, blocks) == [[] for _ in range(7)]


def test_carry_into_stacks_overflow_from_several_days():
    blocks = {WEEK[0]: ["easy"] * (DAY_BLOCKS + 2),   # 2 over
              WEEK[1]: ["hard"] * (DAY_BLOCKS + 1)}   # +2 carried, so 3 over
    assert carry_into(WEEK[2], blocks) == ["hard"] * 3
    assert carry_into(WEEK[0], blocks) == []          # nothing before the first solve


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
    assert ws["carry_out"] == 0


def test_weekly_streak_reports_blocks_carried_into_next_week(monkeypatch):
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 26, 12, tzinfo=tz)  # Friday

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    blocks = {WEEK[5]: ["medium"] * (DAY_BLOCKS * 2 + 4)}  # Fri, Sat, +4 for Sunday
    ws = weekly_streak({WEEK[5]: DAY_BLOCKS * 2 + 4}, blocks, UTC)
    assert [d["met"] for d in ws["days"][5:]] == [True, True]
    assert ws["carry_out"] == 4


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


def test_month_calendar_sunday_completed_by_last_weeks_overflow(monkeypatch):
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 30, 12, tzinfo=tz)

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    blocks = {WEEK[6]: ["hard"] * (DAY_BLOCKS * 2)}  # Sat 27 June, a day over
    weeks = month_calendar(blocks, UTC, 2026, 6)["weeks"]
    sat_27, sun_28 = weeks[3][6], weeks[4][0]
    assert (sat_27["day"], sat_27["done"]) == (27, True)
    assert (sun_28["day"], sun_28["done"]) == (28, True)
    assert weeks[4][1]["done"] is False              # Monday: the carry ran out


def test_month_calendar_marks_future_days_overflow_already_fills(monkeypatch):
    """Future days are never `done`, but ones the carry already covers are
    `prefilled` (the lighter dot) — and only those."""
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 26, 12, tzinfo=tz)  # Friday

    monkeypatch.setattr(progress, "datetime", _FixedDT)
    blocks = {WEEK[5]: ["medium"] * (DAY_BLOCKS * 3 + 4)}  # Fri + Sat + Sun, 4 on Mon
    weeks = month_calendar(blocks, UTC, 2026, 6)["weeks"]
    fri, sat = weeks[3][5], weeks[3][6]
    sun, mon = weeks[4][0], weeks[4][1]
    assert (fri["day"], fri["done"], fri["prefilled"]) == (26, True, False)
    assert (sat["day"], sat["done"], sat["prefilled"]) == (27, False, True)
    assert (sun["day"], sun["done"], sun["prefilled"]) == (28, False, True)
    assert (mon["day"], mon["done"], mon["prefilled"]) == (29, False, False)  # 4 of 8


def test_month_calendar_marks_days_short_of_the_goal_partial(monkeypatch):
    """A day with some blocks but not a full day is `partial` with its count —
    past, today and an overflow-queued future day alike; full and empty days
    (and adjacent-month cells) are not."""
    import app.progress as progress

    class _FixedDT(progress.datetime):
        @classmethod
        def now(cls, tz=None):
            return progress.datetime(2026, 6, 24, 12, tzinfo=tz)  # Wednesday

    monkeypatch.setattr(progress, "datetime", _FixedDT)

    def cells(blocks):
        weeks = month_calendar(blocks, UTC, 2026, 6)["weeks"]
        return weeks[0][0], {c["day"]: (c["partial"], c["filled"])
                             for wk in weeks for c in wk if c["in_month"]}

    may_31, june = cells({
        date(2026, 5, 31): ["easy"] * 2,          # adjacent month: stays blank
        WEEK[1]: ["easy"] * 3,                    # Mon 22 (past): 3 of 8
        WEEK[2]: ["medium"] * DAY_BLOCKS,         # Tue 23 (past): exactly a day
        WEEK[3]: ["hard"] * (DAY_BLOCKS + 4),     # Wed 24 (today): spills 4 to Thu
    })
    assert june[22] == (True, 3)
    assert june[23] == (False, DAY_BLOCKS)
    assert june[24] == (False, DAY_BLOCKS)
    assert june[25] == (True, 4)                  # future, half a day queued
    assert june[26] == (False, 0)
    assert (may_31["in_month"], may_31["partial"]) == (False, False)

    _, june = cells({WEEK[3]: ["easy"] * 5})      # today, still short
    assert june[24] == (True, 5)


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
