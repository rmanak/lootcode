"""End-to-end app tests via FastAPI's TestClient (uses the real executor)."""
import re

import pytest
from fastapi.testclient import TestClient

from app.main import app

CANONICAL = (
    "def twoSum(nums, target):\n"
    "    seen = {}\n"
    "    for i, n in enumerate(nums):\n"
    "        if target - n in seen:\n"
    "            return [seen[target - n], i]\n"
    "        seen[n] = i\n"
    "    return []\n"
)


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:  # context manager runs startup (init_db + seed)
        yield c


def test_home_lists_problems(client):
    r = client.get("/")
    assert r.status_code == 200
    assert 'class="problems"' in r.text
    # Two Sum sits deep in the (alphabetical) bank, so it lives on a later page;
    # a title search surfaces it regardless of pagination.
    assert "Two Sum" in client.get("/?q=Two+Sum").text


def test_problem_page_has_editor(client):
    r = client.get("/problems/two-sum")
    assert r.status_code == 200
    assert 'id="code"' in r.text and "twoSum" in r.text


def test_filters_and_pages_ok(client):
    assert client.get("/?difficulty=easy&topic=array").status_code == 200
    assert client.get("/me").status_code == 200
    assert client.get("/admin").status_code == 200


def test_pagination(client):
    r = client.get("/")
    assert 'class="pagination"' in r.text  # bank is large enough to paginate
    # Different pages show different problems...
    assert client.get("/?page=1").text != client.get("/?page=2").text
    # ...and an out-of-range page clamps to the last page instead of erroring.
    assert client.get("/?page=99999").status_code == 200


def test_unsolved_filter(client):
    r = client.get("/?unsolved=1")
    assert r.status_code == 200
    # The status chip reflects the active filter, and other filters still combine.
    assert "status-chip active" in r.text
    assert client.get("/?unsolved=1&difficulty=easy&q=sum").status_code == 200


def test_unknown_filter_and_marking(client):
    # Marking a problem "known" flips the API state and then hides it from the
    # "unknown only" list (and from the random-jump pool). Two Sum lives deep in
    # the alphabetical bank, so search for it to dodge pagination.
    assert client.post("/api/problems/two-sum/known",
                       json={"known": True}).json() == {"known": True}
    r = client.get("/?unknown=1&q=Two+Sum")
    assert r.status_code == 200
    assert "status-chip unknown active" in r.text
    assert 'href="/problems/two-sum"' not in r.text
    # Unmarking brings it back.
    assert client.post("/api/problems/two-sum/known",
                       json={"known": False}).json() == {"known": False}
    assert 'href="/problems/two-sum"' in client.get("/?unknown=1&q=Two+Sum").text


def test_visit_later_filter_and_marking(client):
    # Flagging a problem "visit later" flips the API state, then the "Visit later"
    # filter shows only flagged problems (and the chip reflects it). Two Sum lives
    # deep in the bank, so a title search dodges pagination.
    assert client.get("/?visit_later=1&q=Two+Sum").text.count(
        'href="/problems/two-sum"') == 0
    assert client.post("/api/problems/two-sum/visit-later",
                       json={"visit_later": True}).json() == {"visit_later": True}
    r = client.get("/?visit_later=1&q=Two+Sum")
    assert r.status_code == 200
    assert "status-chip later active" in r.text
    assert 'href="/problems/two-sum"' in r.text
    # Combines with other filters just like the status chips do.
    assert client.get("/?visit_later=1&difficulty=easy&q=Two+Sum").status_code == 200
    # Unflagging removes it from the filtered list again.
    assert client.post("/api/problems/two-sum/visit-later",
                       json={"visit_later": False}).json() == {"visit_later": False}
    assert 'href="/problems/two-sum"' not in client.get(
        "/?visit_later=1&q=Two+Sum").text


def test_collection_filter_lists_members_in_study_order(client):
    r = client.get("/?collection=blind-73")
    assert r.status_code == 200
    # The active-list banner names the list.
    assert "collection-banner" in r.text and "Blind 73" in r.text
    # Members show; a non-member (gas-station isn't in Blind 73) does not.
    assert 'href="/problems/two-sum"' in r.text
    assert 'href="/problems/gas-station"' not in r.text
    # Curated study order, not id/alphabetical: #1 precedes #2 on the first page.
    assert (r.text.index("/problems/longest-consecutive-sequence")
            < r.text.index("/problems/two-sum"))


def test_collection_chip_on_home(client):
    r = client.get("/")
    assert "list-chip" in r.text and "Blind 73" in r.text


def test_collection_composes_and_tolerates_unknown_slug(client):
    # Composes with other filters.
    assert client.get("/?collection=blind-73&difficulty=easy").status_code == 200
    # A stale/unknown collection slug is treated as "no list filter" (no empty
    # page, no banner) rather than a 404.
    r = client.get("/?collection=nope-not-real")
    assert r.status_code == 200 and "collection-banner" not in r.text


def test_seed_collections_skips_unknown_slug(client, monkeypatch):
    # A manifest slug that doesn't resolve to a problem is skipped + reported,
    # never fatal. (Cleans up the temp collection it writes.)
    from sqlalchemy import select

    from app import content, store
    from app.db import SessionLocal
    from app.models import Collection

    fake = [{"slug": "t-test-list", "title": "T", "subtitle": "",
             "problems": ["two-sum", "definitely-not-a-real-slug-xyz"]}]
    monkeypatch.setattr(content, "load_collections", lambda *a, **k: fake)
    with SessionLocal() as db:
        try:
            _, unresolved = store.seed_collections(db)
            assert "t-test-list:definitely-not-a-real-slug-xyz" in unresolved
            assert len(store.collection_member_ids(db, "t-test-list")) == 1
        finally:
            c = db.scalar(select(Collection).where(Collection.slug == "t-test-list"))
            if c:
                db.delete(c)
                db.commit()


def test_run_canonical_full_score(client):
    r = client.post("/api/problems/two-sum/run", json={"code": CANONICAL})
    assert r.status_code == 200
    d = r.json()
    assert d["solved"] is True
    assert d["passed_count"] == d["total_count"] == 6
    assert d["score"] == 100


def test_run_accepts_tab_indentation(client):
    # Mixed tab/space indentation used to raise a Python TabError; the server
    # now expands tabs to spaces before executing.
    tabbed = (
        "def twoSum(nums, target):\n"
        "\tseen = {}\n"
        "\tfor i, n in enumerate(nums):\n"
        "\t\tif target - n in seen:\n"
        "\t\t\treturn [seen[target - n], i]\n"
        "\t\tseen[n] = i\n"
        "\treturn []\n"
    )
    r = client.post("/api/problems/two-sum/run", json={"code": tabbed})
    assert r.status_code == 200
    d = r.json()
    assert d["solved"] is True
    assert d["passed_count"] == d["total_count"] == 6


def test_hidden_tests_not_leaked(client):
    r = client.post("/api/problems/two-sum/run",
                    json={"code": "def twoSum(nums, target):\n    return [0, 0]\n"})
    d = r.json()
    assert d["solved"] is False
    hidden = [x for x in d["results"] if x["hidden"]]
    assert hidden
    assert all("stdout" not in x and "error" not in x for x in hidden)


def test_progress_links_submission_into_editor(client):
    # Submitting saves the code; the progress page links each submission's date to
    # the problem page with that submission loaded into the editor.
    marker = "def twoSum(nums, target):\n    # mysubmissionmarker\n    return [0, 1]\n"
    client.post("/api/problems/two-sum/run", json={"code": marker})

    me = client.get("/me").text
    m = re.search(r'href="(/problems/two-sum\?submission=[0-9a-f]+)"', me)
    assert m, "progress page should link the submission date back to the editor"

    page = client.get(m.group(1)).text
    assert "mysubmissionmarker" in page          # editor pre-filled with our code
    assert "Loaded your submission" in page      # and the note tells the user so


def test_cannot_load_another_users_submission(client):
    # Make a submission as the default identity, grab its id...
    r = client.post("/api/problems/two-sum/run",
                    json={"code": "def twoSum(nums, target):\n    # privatecode\n    return []\n"})
    assert r.status_code == 200
    me = client.get("/me").text
    sub_id = re.search(r"submission=([0-9a-f]+)", me).group(1)

    # ...then a *fresh* client (new cookie => new user) must not see that code; it
    # falls back to the starter solution instead of leaking another user's code.
    with TestClient(app) as other:
        page = other.get(f"/problems/two-sum?submission={sub_id}").text
        assert "privatecode" not in page
        assert "Loaded your submission" not in page


def test_quick_picks_on_both_pages(client):
    # The "jump to a random unsolved" picks (with the highlighted arrow) appear
    # on the problem list and the progress page, and the buttons link to /random.
    for path in ("/", "/me"):
        t = client.get(path).text
        assert "Jump to a random unsolved problem" in t
        assert 'class="qp-arrow"' in t
        assert 'href="/random/easy"' in t


def test_weekly_streak_counts_solves(client):
    # Solving an (easy) problem credits this week with its unit weight, once.
    client.post("/api/problems/two-sum/run", json={"code": CANONICAL})
    me = client.get("/me").text
    assert "This week" in me
    # Sun–Sat columns rendered (weekend included).
    assert re.search(r"streak-label\">Sun<", me)
    assert re.search(r"streak-label\">Sat<", me)
    assert "/7 days hit the goal" in me
    total = int(re.search(r"(\d+) units total", me).group(1))
    assert total >= 1
    # A second submission of the same solved problem must not double count.
    client.post("/api/problems/two-sum/run", json={"code": CANONICAL})
    again = int(re.search(r"(\d+) units total", client.get("/me").text).group(1))
    assert again == total


def test_user_tz_decodes_percent_encoded_cookie():
    # The client sets lc_tz via encodeURIComponent, so a slashed IANA name
    # arrives percent-encoded; Starlette does not decode cookie values, so the
    # server must unquote it. Otherwise every real zone silently became UTC and
    # an evening solve rolled into the next UTC day. Regression guard.
    from zoneinfo import ZoneInfo
    from starlette.requests import Request

    from app.routers.pages import _user_tz

    def tz_for(value: str) -> ZoneInfo:
        header = ("lc_tz=" + value).encode()
        return _user_tz(Request({"type": "http", "headers": [(b"cookie", header)]}))

    assert tz_for("America%2FNew_York") == ZoneInfo("America/New_York")
    assert tz_for("Europe/London") == ZoneInfo("Europe/London")  # unencoded too
    # Garbage / hostile values fall back to UTC instead of raising.
    for bad in ("%2E%2E%2Fetc%2Fpasswd", "Not/A/Zone", "", "%ZZ"):
        assert tz_for(bad) == ZoneInfo("UTC")


def test_calendar_green_matches_weekly_met_with_spillover():
    # A day completed only via spillover (yesterday overflowed into today) must
    # show ✓ in the weekly grid AND a green dot on the month calendar — the two
    # views shared no completion logic before and disagreed. Regression guard.
    from datetime import date

    from app.routers.pages import DAY_BLOCKS, _lay_out_week, _month_calendar

    # Sunday gets 1.5 days of work; the half-day overflow pre-fills Monday, which
    # has only a partial day of its own — so Monday hits the goal only via carry.
    sunday, monday = date(2026, 6, 21), date(2026, 6, 22)
    blocks = {
        sunday: ["hard"] * (DAY_BLOCKS + DAY_BLOCKS // 2),  # fills Sun, spills half
        monday: ["hard"] * (DAY_BLOCKS // 2),               # own work < a full day
    }
    week = [date(2026, 6, 21 + i) for i in range(7)]  # Sun … Sat
    placed = _lay_out_week(week, blocks)
    assert len(placed[0]) >= DAY_BLOCKS                       # Sunday met
    assert len(blocks[monday]) < DAY_BLOCKS                   # Monday own < goal
    assert len(placed[1]) >= DAY_BLOCKS                       # Monday met via carry

    # The calendar must mark Monday done too (pretend "today" is later so it's past).
    from zoneinfo import ZoneInfo
    import app.routers.pages as pages

    class _FixedDT(pages.datetime):
        @classmethod
        def now(cls, tz=None):
            return pages.datetime(2026, 6, 30, 12, tzinfo=tz)

    orig = pages.datetime
    pages.datetime = _FixedDT
    try:
        mc = _month_calendar(blocks, ZoneInfo("UTC"), 2026, 6)
    finally:
        pages.datetime = orig
    done = {c["day"]: c["done"] for wk in mc["weeks"] for c in wk if c["in_month"]}
    assert done[21] is True and done[22] is True
