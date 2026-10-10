"""The assessment flow over HTTP: start, run, submit, gate, clock, report."""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest

from icf.db import session
from icf.models import Attempt

from .conftest import TOY_SLUG

pytestmark = pytest.mark.slow

GOOD = '''class Counter:
    def __init__(self):
        self._values = []

    def add(self, n):
        self._values.append(n)
        return len(self._values)

    def total(self):
        return sum(self._values)

    def undo(self):
        if not self._values:
            return False
        self._values.pop()
        return True

    def label(self):
        return "+".join(str(v) for v in self._values)
'''


def start(client, mode="exam"):
    resp = client.post(f"/api/icf/{TOY_SLUG}/attempts", json={"mode": mode})
    assert resp.status_code == 200, resp.text
    return resp.json()["attempt"]


def test_the_list_page_shows_installed_problems(icf_client):
    body = icf_client.get("/icf").text
    assert "Toy Counter" in body
    assert f'href="/icf/{TOY_SLUG}"' in body


def test_an_unknown_problem_is_a_404(icf_client):
    assert icf_client.get("/icf/not-a-problem").status_code == 404


def test_opening_the_workspace_does_not_start_the_clock(icf_client):
    body = icf_client.get(f"/icf/{TOY_SLUG}").text
    assert "Start assessment" in body, "the page should offer to start, not start"
    with session() as db:
        assert db.query(Attempt).count() == 0


def test_starting_twice_returns_the_same_attempt(icf_client):
    first = start(icf_client)
    second = start(icf_client)
    assert first["id"] == second["id"], "a double-click must not reset the clock"


def test_an_exam_attempt_has_a_clock_and_practice_does_not(icf_client, new_browser):
    exam = start(icf_client)
    assert 0 < exam["remaining_ms"] <= 90 * 60 * 1000
    other = new_browser()
    assert start(other, "practice")["remaining_ms"] is None


def test_only_level_one_is_unlocked_at_the_start(icf_client):
    levels = start(icf_client)["levels"]
    assert [lv["unlocked"] for lv in levels] == [True, False, False, False]


def test_a_locked_level_cannot_be_submitted(icf_client):
    attempt = start(icf_client)
    resp = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 3, "code": GOOD})
    assert resp.status_code == 403
    assert "locked" in resp.json()["detail"]


def test_a_run_does_not_unlock_the_next_level(icf_client):
    attempt = start(icf_client)
    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/run",
                           json={"level": 1, "code": GOOD}).json()
    assert data["run"]["all_passed"]
    assert data["unlocked_level"] is None, "hidden tests have not been run yet"
    assert data["attempt"]["levels"][1]["unlocked"] is False


def test_a_submit_that_passes_unlocks_the_next_level(icf_client):
    attempt = start(icf_client)
    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 1, "code": GOOD}).json()
    assert data["unlocked_level"] == 2
    assert data["attempt"]["levels"][0]["passed"] is True
    assert data["attempt"]["highest_level_passed"] == 1


def test_a_failing_submit_unlocks_nothing(icf_client):
    attempt = start(icf_client)
    broken = GOOD.replace("        return len(self._values)", "        return 99")
    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 1, "code": broken}).json()
    assert not data["run"]["all_passed"]
    assert data["unlocked_level"] is None
    assert data["attempt"]["levels"][1]["unlocked"] is False


def test_hidden_cases_reveal_nothing_but_a_verdict(icf_client):
    attempt = start(icf_client)
    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 1, "code": GOOD}).json()
    hidden = [c for lv in data["run"]["levels"] for c in lv["cases"] if c["hidden"]]
    assert hidden, "level 1 has a hidden case"
    for case in hidden:
        assert case["label"].startswith("Hidden test")
        assert set(case) == {"hidden", "label", "status", "passed"}


def test_submitting_a_level_re_runs_every_level_below_it(icf_client):
    attempt = start(icf_client)
    icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                    json={"level": 1, "code": GOOD})
    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 2, "code": GOOD}).json()
    assert [lv["level"] for lv in data["run"]["levels"]] == [1, 2]


def test_the_whole_ladder_can_be_climbed(icf_client):
    attempt = start(icf_client)
    for level in (1, 2, 3, 4):
        data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                               json={"level": level, "code": GOOD}).json()
        assert data["run"]["all_passed"], (level, data["run"])
    assert data["attempt"]["highest_level_passed"] == 4
    assert data["attempt"]["status"] == "finished", "passing level 4 ends the sitting"


def test_the_editor_buffer_is_saved_and_comes_back(icf_client):
    attempt = start(icf_client)
    icf_client.post(f"/api/icf/attempts/{attempt['id']}/draft",
                    json={"code": "class Counter:\n    # my work\n    pass\n"})
    assert "# my work" in icf_client.get(f"/icf/{TOY_SLUG}").text


def test_a_run_after_the_clock_expires_is_recorded_but_inert(icf_client):
    attempt = start(icf_client)
    with session() as db:
        row = db.get(Attempt, attempt["id"])
        row.expires_at = datetime.now(UTC) - timedelta(seconds=1)
        db.commit()

    data = icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                           json={"level": 1, "code": GOOD}).json()
    assert data["late"] is True
    assert data["run"]["all_passed"], "it is still graded and shown"
    assert data["unlocked_level"] is None, "but it may not open level 2"
    assert data["attempt"]["status"] == "expired"
    assert data["attempt"]["levels"][1]["unlocked"] is False


def test_an_attempt_belongs_to_one_visitor(icf_client, new_browser):
    attempt = start(icf_client)
    stranger = new_browser()
    assert stranger.get(f"/api/icf/attempts/{attempt['id']}").status_code == 404
    assert stranger.get(f"/icf/attempts/{attempt['id']}").status_code == 404


def test_finishing_stops_the_attempt_and_the_report_renders(icf_client):
    attempt = start(icf_client)
    icf_client.post(f"/api/icf/attempts/{attempt['id']}/submit",
                    json={"level": 1, "code": GOOD})
    finished = icf_client.post(f"/api/icf/attempts/{attempt['id']}/finish").json()
    assert finished["attempt"]["status"] == "finished"

    page = icf_client.get(f"/icf/attempts/{attempt['id']}")
    assert page.status_code == 200
    assert "level 1/4" in page.text
    assert "25" in page.text, "one level of four is 25 points"


def test_an_empty_submission_is_refused(icf_client):
    attempt = start(icf_client)
    resp = icf_client.post(f"/api/icf/attempts/{attempt['id']}/run",
                           json={"level": 1, "code": "   "})
    assert resp.status_code == 400
