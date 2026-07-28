"""Regression tests for the correctness and reliability fixes.

Each of these pins a bug that was real and, in most cases, silent — the kind
that a passing test suite would otherwise never notice coming back.
"""
from __future__ import annotations

import pytest
from sqlalchemy import select, text

from app import main as app_main
from app.config import settings
from app.content import owning_root, write_problem_files
from app.db import engine

# TestResult is aliased away from a `Test*` name so pytest doesn't try to
# collect the ORM model as a test class.
from app.models import Submission, User
from app.models import TestResult as ResultRow
from app.routers.submissions import MAX_CODE_CHARS, MAX_STORED_STDOUT

SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="10" height="10"></svg>'


def _problem(slug: str, **over) -> dict:
    data = {
        "slug": slug, "title": slug.replace("-", " ").title(), "difficulty": "easy",
        "topics": ["math"], "hints": [], "statement_md": "Return `a + b`.",
        "kind": "function", "function_name": "addTwo",
        "params": [{"name": "a", "type": "int"}, {"name": "b", "type": "int"}],
        "return_type": "int", "compare": "exact",
        "starter_code": "def addTwo(a, b):\n    pass\n",
        "canonical_solution": "def addTwo(a, b):\n    return a + b\n",
        "scoring_type": "weighted", "points": 100,
        "class_name": None, "class_methods": None,
        "tests": [{"name": "c1", "input": {"a": 1, "b": 2}, "expected": 3,
                   "weight": 1, "hidden": False}],
    }
    data.update(over)
    return data


# --- #1 figures in the extended root were 404ing ------------------------
def test_a_figure_in_the_extended_root_is_served(client, tmp_content_dir):
    """Assets resolved only under CONTENT_DIR, so every figure belonging to a
    problem in content/problems-extended/ 404'd while its statement still
    rendered the <img>."""
    extended = tmp_content_dir.parent / "problems-extended"
    write_problem_files(_problem("zz-extended-fig", assets={"fig.svg": SVG}), extended)

    r = client.get("/problems/zz-extended-fig/assets/fig.svg")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("image/svg+xml")
    assert r.text == SVG


def test_a_figure_in_the_default_root_still_works(client, tmp_content_dir):
    write_problem_files(_problem("zz-default-fig", assets={"fig.svg": SVG}),
                        tmp_content_dir)
    assert client.get("/problems/zz-default-fig/assets/fig.svg").status_code == 200


@pytest.mark.parametrize("path", [
    "/problems/two-sum/assets/..%2F..%2Fmeta.json",
    "/problems/..%2Ftwo-sum/assets/fig.svg",
    "/problems/two-sum/assets/solution.py",
    "/problems/two-sum/assets/nope.svg",
])
def test_the_multi_root_search_did_not_widen_the_traversal_guard(client, path):
    assert client.get(path).status_code == 404


# --- #2 admin edits wrote a duplicate into the wrong content root --------
def test_editing_an_extended_problem_writes_back_to_the_extended_root(tmp_content_dir):
    extended = tmp_content_dir.parent / "problems-extended"
    write_problem_files(_problem("zz-owned-by-extended"), extended)

    assert owning_root("zz-owned-by-extended") == extended
    # ...and the default root is untouched, which is the actual bug: a save used
    # to create a second, git-tracked copy there.
    assert not (tmp_content_dir / "zz-owned-by-extended").exists()


def test_a_problem_in_the_default_root_resolves_to_it(tmp_content_dir):
    write_problem_files(_problem("zz-owned-by-default"), tmp_content_dir)
    assert owning_root("zz-owned-by-default") == tmp_content_dir


def test_a_brand_new_problem_goes_to_the_default_root(tmp_content_dir):
    assert owning_root("zz-does-not-exist-anywhere") == settings.CONTENT_DIR


# --- #3 a failed disk mirror was swallowed -------------------------------
def test_a_failed_disk_mirror_is_reported_not_swallowed(client, db, tmp_content_dir,
                                                        monkeypatch):
    """`except OSError: pass` let a full disk or a read-only mount desync the DB
    from the durable source of truth with no log line and nothing shown."""
    import app.routers.admin_problems as admin_mod

    def read_only(*a, **kw):
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(admin_mod.content, "write_problem_files", read_only)

    import json as _json

    r = client.post("/admin/new", data={
        "slug": "zz-mirror-fails", "title": "ZZ Mirror Fails", "difficulty": "easy",
        "topics": "math", "hints": "", "statement_md": "Return `a + b`.",
        "kind": "function", "function_name": "addTwo",
        "params": "a: int\nb: int", "return_type": "int", "compare": "exact",
        "starter_code": "def addTwo(a, b):\n    pass\n",
        "canonical_solution": "def addTwo(a, b):\n    return a + b\n",
        "tests_json": _json.dumps([
            {"name": f"c{i}", "input": {"a": i, "b": 1}, "expected": i + 1,
             "weight": 1, "hidden": i > 0} for i in range(4)]),
        "source": "test", "class_name": "", "class_methods_json": "[]",
    }, follow_redirects=False)

    assert r.status_code == 200, "must render, not redirect as if all was well"
    assert "Read-only file system" in r.text
    assert "out of step" in r.text


# --- #4/#8 the identity middleware ---------------------------------------
def test_a_page_request_still_mints_exactly_one_guest(client):
    client.cookies.clear()
    before = _user_count()
    client.get("/")
    assert _user_count() == before + 1
    # A second request reuses the cookie rather than minting again.
    client.get("/")
    assert _user_count() == before + 1


@pytest.mark.parametrize("path", [
    "/wp-login.php", "/.env", "/some/random/404", "/favicon.ico",
    "/static/app.css",
    # A plain `startswith("/admin")` matches this. Found by pointing a scanner's
    # worth of paths at a real server, not by the check above.
    "/admin.php", "/administrator", "/api-docs.bak", "/logout.php",
])
def test_bots_and_404s_no_longer_mint_a_user_row(client, path):
    """Every request without a valid cookie used to create a guest — one row per
    crawler hit and per 404, forever, each one a write on the request path."""
    client.cookies.clear()
    before = _user_count()
    client.get(path)
    assert _user_count() == before


def test_identity_paths_are_the_ones_that_render_for_a_person():
    for path in ("/", "/problems/two-sum", "/api/problems/two-sum/run",
                 "/admin", "/admin/new", "/me", "/account", "/random/easy"):
        assert app_main._wants_identity(path), path
    for path in ("/static/app.css", "/favicon.ico", "/wp-login.php",
                 # The prefix check is segment-wise, so these are scanner noise,
                 # not admin traffic.
                 "/admin.php", "/administrator", "/api-docs.bak", "/logout.php",
                 "/robots.txt", "/.git/config"):
        assert not app_main._wants_identity(path), path


def _user_count() -> int:
    from sqlalchemy import func

    from app.db import SessionLocal

    with SessionLocal() as s:
        return s.scalar(select(func.count()).select_from(User))


# --- #5 SQLite pragmas ----------------------------------------------------
def test_the_connection_is_configured_for_a_threaded_server():
    with engine.connect() as conn:
        assert conn.exec_driver_sql("PRAGMA journal_mode").scalar().lower() == "wal"
        assert conn.exec_driver_sql("PRAGMA busy_timeout").scalar() == 5000
        assert conn.exec_driver_sql("PRAGMA foreign_keys").scalar() == 1


def test_foreign_keys_are_enforced_not_just_by_the_orm():
    with engine.begin() as conn:
        with pytest.raises(Exception):  # noqa: B017 - any IntegrityError subclass
            conn.execute(text(
                "INSERT INTO test_results "
                "(submission_id, name, hidden, passed, status, time_ms) "
                "VALUES (-12345, 'x', 0, 0, 'error', 0)"))


# --- #6/#7 grading holds no session; code and stdout are bounded ---------
@pytest.mark.slow
def test_a_run_holds_no_database_session_while_the_sandbox_runs(client, monkeypatch):
    """The session used to be checked out for the whole (up to ~15 s) grade."""
    import app.routers.submissions as subs

    open_sessions = []
    real = subs.run_submission

    def watching(code, view, tests):
        # sqlalchemy's pool reports how many connections are checked out.
        open_sessions.append(engine.pool.checkedout())
        return real(code, view, tests)

    monkeypatch.setattr(subs, "run_submission", watching)
    client.cookies.clear()
    client.get("/")
    r = client.post("/api/problems/two-sum/run", json={
        "code": "def twoSum(nums, target):\n"
                "    seen = {}\n"
                "    for i, n in enumerate(nums):\n"
                "        if target - n in seen:\n"
                "            return [seen[target - n], i]\n"
                "        seen[n] = i\n"
                "    return []\n"})
    assert r.status_code == 200 and r.json()["solved"] is True
    assert open_sessions == [0], "no connection may be checked out during grading"


def test_an_oversized_submission_is_refused_before_it_reaches_the_database(client):
    client.cookies.clear()
    client.get("/")
    r = client.post("/api/problems/two-sum/run",
                    json={"code": "#" * (MAX_CODE_CHARS + 1)})
    assert r.status_code == 422


@pytest.mark.slow
def test_stored_stdout_is_capped(client):
    """stdout was capped at 4,000 chars on the way out but stored uncapped, so a
    print-in-a-loop solution wrote megabytes per test into SQLite."""
    from app.db import SessionLocal

    client.cookies.clear()
    client.get("/")
    uid = client.cookies.get("lc_uid")
    noisy = ("def twoSum(nums, target):\n"
             "    print('x' * 200000)\n"
             "    return []\n")
    r = client.post("/api/problems/two-sum/run", json={"code": noisy})
    assert r.status_code == 200

    with SessionLocal() as s:
        sub = s.scalars(select(Submission).where(Submission.user_id == uid)
                        .order_by(Submission.id.desc())).first()
        results = list(s.scalars(
            select(ResultRow).where(ResultRow.submission_id == sub.id)))
    assert results
    for tr in results:
        assert len(tr.stdout or "") <= MAX_STORED_STDOUT


# --- the LAN trust boundary ----------------------------------------------
@pytest.mark.parametrize("host", ["127.0.0.1", "localhost", "::1", ""])
def test_a_loopback_bind_starts_without_ceremony(host):
    app_main.check_bind_is_intentional(host)  # must not raise


@pytest.mark.parametrize("host", ["0.0.0.0", "10.8.0.1", "192.168.1.20",
                                  "not-a-known-host"])
def test_a_non_loopback_bind_refuses_to_start(host, monkeypatch, capsys):
    monkeypatch.setattr(settings, "TRUST_LAN", False)
    with pytest.raises(SystemExit) as exc:
        app_main.check_bind_is_intentional(host)
    assert host in str(exc.value)
    assert "LOOTCODE_TRUST_LAN=1" in str(exc.value)
    # The explanation is *printed*, because uvicorn wraps a lifespan exception
    # in a traceback that would bury it.
    err = capsys.readouterr().err
    assert "NO authentication" in err
    assert "does NOT block network access" in err
    assert "docs/security.md" in err


@pytest.mark.parametrize("host", ["0.0.0.0", "10.8.0.1"])
def test_an_opted_in_lan_bind_is_allowed(host, monkeypatch):
    monkeypatch.setattr(settings, "TRUST_LAN", True)
    app_main.check_bind_is_intentional(host)  # must not raise


def test_the_bind_host_is_read_from_uvicorns_own_flags(monkeypatch):
    """`uvicorn app.main:app --host 0.0.0.0` never touches settings.HOST, so the
    guard has to look where the bind actually comes from."""
    monkeypatch.delenv("UVICORN_HOST", raising=False)
    monkeypatch.setattr(app_main.sys, "argv",
                        ["uvicorn", "app.main:app", "--host", "0.0.0.0"])
    assert app_main.effective_bind_host() == "0.0.0.0"

    monkeypatch.setattr(app_main.sys, "argv",
                        ["uvicorn", "app.main:app", "--host=192.168.1.5"])
    assert app_main.effective_bind_host() == "192.168.1.5"

    monkeypatch.setenv("UVICORN_HOST", "10.0.0.9")
    assert app_main.effective_bind_host() == "10.0.0.9"

    monkeypatch.delenv("UVICORN_HOST")
    monkeypatch.setattr(app_main.sys, "argv", ["uvicorn", "app.main:app"])
    assert app_main.effective_bind_host() == settings.HOST
