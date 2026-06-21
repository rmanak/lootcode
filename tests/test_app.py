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
