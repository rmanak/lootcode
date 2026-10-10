"""Public routes that had no test: /random/{difficulty}, /me/name, /account,
POST /api/llm/refresh, GET /api/llm/status, POST /problems/{slug}/help.

The two LLM routes are exercised in both states — endpoint off (the deterministic
case, which is what CI sees) and endpoint on — without ever requiring a live
model: the probe and the stream are stubbed.
"""
import asyncio
import re
import threading

import pytest

from app.config import settings


# --- GET /random/{difficulty} --------------------------------------------
@pytest.mark.parametrize("difficulty", ["easy", "medium", "hard"])
def test_random_redirects_to_a_problem_of_that_difficulty(client, db, difficulty):
    from sqlalchemy import select

    from app.models import Problem

    r = client.get(f"/random/{difficulty}", follow_redirects=False)
    assert r.status_code == 303
    location = r.headers["location"]

    if location.startswith("/problems/"):
        slug = location.removeprefix("/problems/")
        prob = db.scalar(select(Problem).where(Problem.slug == slug))
        assert prob is not None and prob.difficulty == difficulty
    else:
        # Nothing unsolved left — falls back to the filtered list, not a 404.
        assert location == f"/?difficulty={difficulty}&unknown=1"


def test_random_404s_on_an_unknown_difficulty(client):
    assert client.get("/random/impossible").status_code == 404
    assert client.get("/random/Easy").status_code == 404


def test_random_falls_back_to_the_list_when_nothing_is_left(client):
    """A brand-new guest marks every easy problem known, so there is nothing to
    jump to — the route must land on the filtered list, not 404 or 500."""
    from sqlalchemy import select

    from app import store
    from app.db import SessionLocal
    from app.models import Problem

    client.cookies.clear()
    client.get("/")  # mint a guest
    uid = client.cookies.get("lc_uid")

    # Straight through the store: 400-odd HTTP round trips would dominate the
    # suite's runtime, and the route under test is /random, not /known.
    with SessionLocal() as s:
        ids = [p.id for p in s.scalars(select(Problem).where(
            Problem.difficulty == "easy", Problem.is_published.is_(True)))]
        for pid in ids:
            store.set_problem_known(s, uid, pid, True)

    r = client.get("/random/easy", follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"] == "/?difficulty=easy&unknown=1"


# --- POST /me/name --------------------------------------------------------
def test_set_name_updates_the_display_name(client):
    client.cookies.clear()
    client.get("/")
    r = client.post("/me/name", data={"name": "  Ada  "}, follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/me"
    assert "Ada" in client.get("/me").text


def test_set_name_ignores_a_blank_name(client):
    client.cookies.clear()
    client.get("/")
    client.post("/me/name", data={"name": "Ada"})
    client.post("/me/name", data={"name": "   "})
    assert "Ada" in client.get("/me").text


def test_set_name_is_truncated_to_forty_chars(client):
    client.cookies.clear()
    client.get("/")
    client.post("/me/name", data={"name": "x" * 100})
    assert "x" * 41 not in client.get("/me").text


# --- GET /account ---------------------------------------------------------
def test_account_page_renders_for_a_guest(client):
    client.cookies.clear()
    r = client.get("/account")
    assert r.status_code == 200
    assert 'name="username"' in r.text


def test_account_page_shows_an_error_query(client):
    client.cookies.clear()
    r = client.get("/account?error=That+username+is+taken.")
    assert "That username is taken." in r.text


# --- POST /api/llm/refresh ------------------------------------------------
@pytest.fixture
def unthrottled_refresh():
    """Clear the route's replay cache so each test really re-probes."""
    from app.routers import submissions

    submissions._last_refresh.update(at=0.0, result=None)
    yield
    submissions._last_refresh.update(at=0.0, result=None)


def test_llm_refresh_reports_unavailable_when_the_probe_fails(
        client, monkeypatch, unthrottled_refresh):
    from app.llm import help_generator

    monkeypatch.setattr(help_generator, "probe_endpoint", lambda **kw: False)
    r = client.post("/api/llm/refresh")
    assert r.status_code == 200
    body = r.json()
    assert body["available"] is False
    assert body["ai_help_enabled"] is False
    assert body["endpoint"] == settings.LLM_HELP_URL
    # And the process-wide flag really flipped.
    assert settings.llm_help_available is False


def test_llm_refresh_turns_the_features_on_when_the_probe_succeeds(
        client, monkeypatch, unthrottled_refresh):
    from app.llm import help_generator

    monkeypatch.setattr(help_generator, "probe_endpoint", lambda **kw: True)
    body = client.post("/api/llm/refresh").json()
    assert body["available"] is True
    assert body["ai_help_enabled"] is True
    assert body["generation_enabled"] is True


def test_llm_refresh_never_raises_even_if_the_probe_explodes(
        client, monkeypatch, unthrottled_refresh):
    from app.llm import help_generator

    def boom(**kw):
        raise RuntimeError("connection reset")

    monkeypatch.setattr(help_generator, "probe_endpoint", boom)
    r = client.post("/api/llm/refresh")
    assert r.status_code == 200 and r.json()["available"] is False


def test_llm_refresh_replays_its_answer_instead_of_re_probing(
        client, monkeypatch, unthrottled_refresh):
    """The route is unauthenticated, flips a process-wide flag and makes an
    outbound request, so back-to-back calls must not each re-probe."""
    from app.llm import help_generator

    calls = []

    def counting_probe(**kw):
        calls.append(1)
        return True

    monkeypatch.setattr(help_generator, "probe_endpoint", counting_probe)
    first = client.post("/api/llm/refresh").json()
    second = client.post("/api/llm/refresh").json()
    assert first == second
    assert len(calls) == 1, "the second call inside the window must be replayed"


# --- GET /api/llm/status + the background watcher -------------------------
def test_llm_status_reports_the_cached_flag_without_probing(client, monkeypatch):
    """Every open problem page polls this, so it must never reach the endpoint."""
    from app.llm import help_generator

    def no_probe(**kw):
        raise AssertionError("GET /api/llm/status must not probe the endpoint")

    monkeypatch.setattr(help_generator, "probe_endpoint", no_probe)
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "llm_help_available", True)
    assert client.get("/api/llm/status").json() == {
        "available": True, "ai_help_enabled": True, "generation_enabled": True}

    monkeypatch.setattr(settings, "llm_help_available", False)
    assert client.get("/api/llm/status").json()["available"] is False


def test_the_watcher_follows_the_endpoint_up_and_down(monkeypatch):
    """The LLM server starting after lootcode turns the features on, and
    stopping turns them off again — no restart, no button."""
    from app.llm import help_generator

    answers = [True, False, True]
    flag_before_each_probe = []
    exhausted = threading.Event()

    def probe(**kw):  # runs in the watcher's worker thread
        if not answers:
            return True  # script done: hold the last answer until cancelled
        flag_before_each_probe.append(settings.llm_help_available)
        answer = answers.pop(0)
        if not answers:
            exhausted.set()
        return answer

    monkeypatch.setattr(help_generator, "probe_endpoint", probe)
    monkeypatch.setattr(settings, "llm_help_available", False)

    async def drive():
        task = asyncio.create_task(help_generator.watch_availability(0.01))
        while not exhausted.is_set():
            await asyncio.sleep(0.01)
        await asyncio.sleep(0.05)  # let the last answer land
        task.cancel()

    asyncio.run(drive())
    assert flag_before_each_probe == [False, True, False]
    assert settings.llm_help_available is True


def test_the_problem_page_wires_the_ai_buttons_for_live_updates(client, monkeypatch):
    """Both AI buttons sit in an .ai-tip wrapper carrying the same "why it's off"
    hover text in either state — CSS shows it only while the button is disabled,
    so llm_status.js has nothing to flip but the button. No note below, and no
    native `title` copy of the message (it would pop up a second time)."""
    off_msg = "AI help is off: no OpenAI-compatible endpoint answers at LLM_HELP_URL"

    monkeypatch.setattr(settings, "llm_help_available", True)
    on = client.get("/problems/two-sum").text
    assert re.search(r'llm_status\.js[^"]*" data-available="1"', on)
    assert on.count('class="ai-tip') == 2
    assert on.count(f'data-tip="{off_msg}') == 2

    monkeypatch.setattr(settings, "llm_help_available", False)
    off = client.get("/problems/two-sum").text
    assert re.search(r'llm_status\.js[^"]*" data-available="0"', off)
    assert off.count(f'data-tip="{off_msg}') == 2
    assert f'title="{off_msg}' not in off
    assert "ai-help-note" not in off


def test_the_admin_page_offers_a_recheck_button_only_while_generation_is_off(
        client, monkeypatch):
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "llm_help_available", False)
    off = client.get("/admin").text
    assert "data-llm-refresh" in off
    assert "llm_refresh.js" in off, "the button needs its script"

    monkeypatch.setattr(settings, "llm_help_available", True)
    on = client.get("/admin").text
    assert "data-llm-refresh" not in on


# --- POST /problems/{slug}/help ------------------------------------------
def test_ai_help_is_503_when_the_endpoint_is_off(client, monkeypatch):
    monkeypatch.setattr(settings, "llm_help_available", False)
    r = client.post("/api/problems/two-sum/help")
    assert r.status_code == 503


def test_ai_help_404s_for_an_unknown_problem(client, monkeypatch):
    monkeypatch.setattr(settings, "llm_help_available", True)
    assert client.post("/api/problems/no-such-problem/help").status_code == 404


def test_ai_help_streams_sse_deltas_then_done(client, monkeypatch):
    from app.llm import help_generator

    monkeypatch.setattr(settings, "llm_help_available", True)
    monkeypatch.setattr(help_generator, "stream_help",
                        lambda *a, **kw: iter(["Think ", "about ", "hashing."]))

    r = client.post("/api/problems/two-sum/help")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.headers["cache-control"] == "no-cache"
    body = r.text
    assert '"type": "delta"' in body and "hashing." in body
    assert '"type": "done"' in body


def test_ai_help_reports_an_empty_response_as_an_error_frame(client, monkeypatch):
    from app.llm import help_generator

    monkeypatch.setattr(settings, "llm_help_available", True)
    monkeypatch.setattr(help_generator, "stream_help", lambda *a, **kw: iter([]))

    body = client.post("/api/problems/two-sum/help").text
    assert '"type": "error"' in body and "empty response" in body


def test_ai_help_turns_a_mid_stream_failure_into_an_error_frame(client, monkeypatch):
    from app.llm import help_generator

    def exploding(*a, **kw):
        yield "starting"
        raise RuntimeError("model went away")

    monkeypatch.setattr(settings, "llm_help_available", True)
    monkeypatch.setattr(help_generator, "stream_help", exploding)

    body = client.post("/api/problems/two-sum/help").text
    assert '"type": "delta"' in body
    assert '"type": "error"' in body and "model went away" in body
    assert '"type": "done"' not in body
