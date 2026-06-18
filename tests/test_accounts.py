"""Optional accounts (V2): lossless claim, login+merge, logout, validation.

These exercise the guest→account flows without running the executor: a "solved"
submission is inserted directly so the focus stays on identity. See
docs/user-accounts-v2.md.
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from app.db import SessionLocal
from app.main import app
from app.models import Problem, Submission, User


def _uname() -> str:
    return "t_" + uuid.uuid4().hex[:8]


def _record_solved(user_id: str, problem_id: int) -> None:
    """Insert a fully-passing submission for `user_id` (no executor needed)."""
    with SessionLocal() as db:
        db.add(Submission(user_id=user_id, problem_id=problem_id, code="x",
                          status="done", score=100, passed_count=1, total_count=1))
        db.commit()


def _two_problem_ids() -> tuple[int, int]:
    with SessionLocal() as db:
        ids = [p.id for p in db.query(Problem).order_by(Problem.id).limit(2)]
    return ids[0], ids[1]


def _new_guest_uid(client: TestClient) -> str:
    """Hit the app so a guest is minted, and return its cookie id."""
    client.get("/")
    return client.cookies.get("lc_uid")


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_create_account_keeps_guest_progress(client):
    """Claiming an account is lossless: same row, progress retained."""
    uid = _new_guest_uid(client)
    pid, _ = _two_problem_ids()
    _record_solved(uid, pid)

    u = _uname()
    r = client.post("/account", data={"username": u, "password": "password123"},
                    follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/me"
    assert "lc_uid" in r.headers.get("set-cookie", "")

    with SessionLocal() as db:
        user = db.get(User, uid)
        assert user.is_account and user.username == u
        assert db.query(Submission).filter_by(user_id=uid, problem_id=pid).count() == 1

    # Header now reflects the account, and /me shows the signed-in identity.
    assert u in client.get("/").text
    assert "Signed in as" in client.get("/me").text


def test_login_from_new_browser_merges_guest_progress(client):
    """A different browser's guest progress is folded into the account on login."""
    a_uid = _new_guest_uid(client)
    pid_a, pid_b = _two_problem_ids()
    _record_solved(a_uid, pid_a)
    u = _uname()
    client.post("/account", data={"username": u, "password": "password123"})

    with TestClient(app) as other:
        b_uid = _new_guest_uid(other)
        assert b_uid != a_uid
        _record_solved(b_uid, pid_b)  # solved as a guest in this browser

        r = other.post("/login", data={"username": u, "password": "password123"},
                       follow_redirects=False)
        assert r.status_code == 303 and r.headers["location"] == "/me"
        # The browser is now the account…
        assert other.cookies.get("lc_uid") == a_uid

    with SessionLocal() as db:
        assert db.get(User, b_uid) is None  # empty guest row removed
        pids = {s.problem_id for s in db.query(Submission).filter_by(user_id=a_uid)}
        assert {pid_a, pid_b} <= pids       # both solves now under the account


def test_duplicate_username_refused_case_insensitively(client):
    u = _uname()
    client.post("/account", data={"username": u, "password": "password123"})
    with TestClient(app) as other:
        _new_guest_uid(other)
        r = other.post("/account",
                       data={"username": u.upper(), "password": "password123"},
                       follow_redirects=False)
        assert r.status_code == 303 and "/account?error=" in r.headers["location"]
        assert "taken" in other.get(r.headers["location"]).text


def test_duplicate_email_refused(client):
    email = f"{_uname()}@example.com"
    client.post("/account",
                data={"username": _uname(), "password": "password123", "email": email})
    with TestClient(app) as other:
        _new_guest_uid(other)
        r = other.post("/account",
                       data={"username": _uname(), "password": "password123",
                             "email": email.upper()},
                       follow_redirects=False)
        assert "/account?error=" in r.headers["location"]
        assert "already in use" in other.get(r.headers["location"]).text


def test_short_password_refused(client):
    _new_guest_uid(client)
    r = client.post("/account", data={"username": _uname(), "password": "short"},
                    follow_redirects=False)
    assert "/account?error=" in r.headers["location"]
    assert "at least" in client.get(r.headers["location"]).text


def test_login_wrong_password_refused(client):
    u = _uname()
    client.post("/account", data={"username": u, "password": "password123"})
    with TestClient(app) as other:
        _new_guest_uid(other)
        r = other.post("/login", data={"username": u, "password": "wrongpass1"},
                       follow_redirects=False)
        assert "/account?error=" in r.headers["location"]
        assert "Wrong username or password" in other.get(r.headers["location"]).text


def test_logout_returns_to_fresh_guest(client):
    uid = _new_guest_uid(client)
    u = _uname()
    client.post("/account", data={"username": u, "password": "password123"})
    r = client.post("/logout", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/"

    home = client.get("/")
    assert client.cookies.get("lc_uid") != uid       # a brand-new guest
    assert "Log in / Sign up" in home.text           # header back to guest CTA
