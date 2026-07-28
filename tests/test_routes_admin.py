"""The /admin surface and the AI-generation routes.

16 of 17 /admin routes had no test — including `POST /admin/new`, the only
validated save path in the app, and `POST /admin/problems/{slug}/edit`, which
rewrites a problem in the bank *and* on disk.

Everything here writes into the temp database and a temp content root, never the
real bank: `tmp_content_dir` redirects `settings.CONTENT_DIR` for the duration of
a test, so a save lands in tmp_path.
"""
import json

import pytest
from sqlalchemy import select

from app.models import Problem

CANONICAL = "def addTwo(a, b):\n    return a + b\n"

TESTS_JSON = json.dumps([
    {"name": "c1", "input": {"a": 1, "b": 2}, "expected": 3,
     "weight": 1, "hidden": False},
    {"name": "c2", "input": {"a": -5, "b": 5}, "expected": 0,
     "weight": 1, "hidden": True},
    {"name": "c3", "input": {"a": 0, "b": 0}, "expected": 0,
     "weight": 1, "hidden": True},
    {"name": "c4", "input": {"a": -7, "b": -8}, "expected": -15,
     "weight": 1, "hidden": True},
])


def form(**over) -> dict:
    """The 14-key form body `POST /admin/new` and `.../edit` both take."""
    data = {
        "slug": "zz-add-two", "title": "ZZ Add Two", "difficulty": "easy",
        "topics": "math", "hints": "Think about it.", "statement_md": "Return `a + b`.",
        "kind": "function", "function_name": "addTwo",
        "params": "a: int\nb: int", "return_type": "int", "compare": "exact",
        "starter_code": "def addTwo(a, b):\n    pass\n",
        "canonical_solution": CANONICAL, "tests_json": TESTS_JSON, "source": "test",
        "class_name": "", "class_methods_json": "[]",
    }
    data.update(over)
    return data


# --- dashboard ------------------------------------------------------------
def test_dashboard_lists_problems(client):
    r = client.get("/admin")
    assert r.status_code == 200
    assert "Problems (" in r.text


def test_dashboard_search_matches_slug_or_title(client):
    assert "two-sum" in client.get("/admin?q=two-sum").text
    assert "Two Sum" in client.get("/admin?q=Two+Sum").text


def test_dashboard_clamps_an_out_of_range_page(client):
    # A stale link must land on the last page, not an empty one.
    r = client.get("/admin?page=99999")
    assert r.status_code == 200
    assert "two-sum" in r.text or "Problems (" in r.text


# --- edit form ------------------------------------------------------------
def test_edit_form_renders_the_stored_problem(client):
    r = client.get("/admin/problems/two-sum/edit")
    assert r.status_code == 200
    assert "twoSum" in r.text


def test_edit_form_404s_for_an_unknown_slug(client):
    assert client.get("/admin/problems/no-such-problem/edit").status_code == 404


# --- create ---------------------------------------------------------------
def test_new_form_renders(client):
    r = client.get("/admin/new")
    assert r.status_code == 200
    assert 'name="slug"' in r.text


@pytest.mark.slow
def test_create_writes_to_the_db_and_to_disk(client, db, tmp_content_dir):
    r = client.post("/admin/new", data=form(), follow_redirects=False)
    assert r.status_code in (200, 303), r.text[:400]

    prob = db.scalar(
        select(Problem).where(Problem.slug == "zz-add-two"))
    assert prob is not None, "the problem should be in the database"

    written = tmp_content_dir / "zz-add-two" / "meta.json"
    assert written.is_file(), "and mirrored to the content root"
    meta = json.loads(written.read_text(encoding="utf-8"))
    assert meta["title"] == "ZZ Add Two"
    assert meta["tags"] == ["math"]


@pytest.mark.slow
def test_create_refuses_an_invented_tag(client, db, tmp_content_dir):
    r = client.post("/admin/new", data=form(slug="zz-bad-tag",
                                            topics="quantum-annealing"))
    assert r.status_code in (200, 400)
    assert "quantum-annealing" in r.text
    assert not (tmp_content_dir / "zz-bad-tag").exists(), "nothing may be written"
    assert db.scalar(
        select(Problem).where(Problem.slug == "zz-bad-tag")) is None


@pytest.mark.slow
def test_create_refuses_a_canonical_that_fails_its_own_tests(client, tmp_content_dir):
    r = client.post("/admin/new", data=form(
        slug="zz-bad-canonical",
        canonical_solution="def addTwo(a, b):\n    return a - b\n"))
    assert "does not pass all of its own tests" in r.text
    assert not (tmp_content_dir / "zz-bad-canonical").exists()


@pytest.mark.slow
def test_create_refuses_a_colliding_slug(client, tmp_content_dir):
    r = client.post("/admin/new", data=form(slug="two-sum"))
    assert "already exists" in r.text


def test_create_refuses_a_malformed_slug(client, tmp_content_dir):
    r = client.post("/admin/new", data=form(slug="Not A Slug"))
    assert "kebab-case" in r.text
    assert not list(tmp_content_dir.iterdir()), "nothing may be written"


def test_create_refuses_unparseable_tests_json(client, tmp_content_dir):
    r = client.post("/admin/new", data=form(tests_json="{not json"))
    assert r.status_code in (200, 400)
    assert not list(tmp_content_dir.iterdir())


# --- edit -----------------------------------------------------------------
@pytest.mark.slow
def test_edit_updates_the_problem(client, db, tmp_content_dir):
    client.post("/admin/new", data=form(slug="zz-edit-me", title="ZZ Edit Me"))
    r = client.post("/admin/problems/zz-edit-me/edit",
                    data=form(slug="zz-edit-me", title="ZZ Renamed"))
    assert r.status_code == 200
    db.expire_all()
    prob = db.scalar(select(Problem).where(Problem.slug == "zz-edit-me"))
    assert prob.title == "ZZ Renamed"


@pytest.mark.slow
def test_edit_rejects_a_bad_change_without_saving(client, db, tmp_content_dir):
    client.post("/admin/new", data=form(slug="zz-keep-me", title="ZZ Keep Me"))
    r = client.post("/admin/problems/zz-keep-me/edit",
                    data=form(slug="zz-keep-me", title="ZZ Keep Me",
                              topics="not-a-real-tag"))
    assert "not-a-real-tag" in r.text
    db.expire_all()
    prob = db.scalar(select(Problem).where(Problem.slug == "zz-keep-me"))
    assert prob.title == "ZZ Keep Me", "the rejected edit must not have landed"


# --- verify (runs submitted code in the sandbox) -------------------------
@pytest.mark.slow
def test_verify_runs_the_submitted_canonical(client):
    body = {"code": CANONICAL, "tests_json": TESTS_JSON, "kind": "function",
            "function_name": "addTwo", "params": "a: int\nb: int",
            "return_type": "int", "compare": "exact",
            "class_name": "", "class_methods_json": "[]"}
    r = client.post("/admin/verify", json=body)
    assert r.status_code == 200
    assert r.json()["solved"] is True


@pytest.mark.slow
def test_verify_reports_a_failing_solution_rather_than_erroring(client):
    body = {"code": "def addTwo(a, b):\n    return a - b\n",
            "tests_json": TESTS_JSON, "kind": "function",
            "function_name": "addTwo", "params": "a: int\nb: int",
            "return_type": "int", "compare": "exact",
            "class_name": "", "class_methods_json": "[]"}
    r = client.post("/admin/verify", json=body)
    assert r.status_code == 200
    assert r.json()["solved"] is False


def test_verify_refuses_empty_code(client):
    r = client.post("/admin/verify", json={
        "code": "   ", "tests_json": TESTS_JSON, "kind": "function",
        "function_name": "addTwo", "params": "", "return_type": "int",
        "compare": "exact", "class_name": "", "class_methods_json": "[]"})
    assert r.status_code == 400


def test_verify_refuses_malformed_tests_json(client):
    r = client.post("/admin/verify", json={
        "code": CANONICAL, "tests_json": "{not json", "kind": "function",
        "function_name": "addTwo", "params": "", "return_type": "int",
        "compare": "exact", "class_name": "", "class_methods_json": "[]"})
    assert r.status_code == 400
    assert "Invalid tests JSON" in r.json()["detail"]


def test_per_problem_verify_shares_the_same_handler(client):
    r = client.post("/admin/problems/two-sum/verify", json={
        "code": "   ", "tests_json": TESTS_JSON, "kind": "function",
        "function_name": "addTwo", "params": "", "return_type": "int",
        "compare": "exact", "class_name": "", "class_methods_json": "[]"})
    assert r.status_code == 400


# --- generation ----------------------------------------------------------
def test_generate_landing_page_renders(client):
    r = client.get("/admin/generate")
    assert r.status_code == 200


def test_generation_routes_refuse_when_the_llm_is_off(client, monkeypatch):
    from app.config import settings

    # Patch the *instance*: refresh_availability() assigns
    # settings.llm_help_available at startup, so a class-level patch is shadowed.
    monkeypatch.setattr(settings, "ANTHROPIC_API_KEY", "")
    monkeypatch.setattr(settings, "llm_help_available", False)
    assert not settings.generation_enabled

    for path, data in (
        ("/admin/generate/statement/stream", {"idea": "x", "difficulty": "easy"}),
        ("/admin/generate/statement", {"idea": "x", "difficulty": "easy"}),
        ("/admin/generate/from-statement", {"statement": "x"}),
    ):
        assert client.post(path, data=data).status_code == 400, path


def test_pasted_statement_is_stored_and_redirects_to_its_page(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "llm_help_available", True)
    r = client.post("/admin/generate/from-statement",
                    data={"statement": "Given two ints, return their sum."},
                    follow_redirects=False)
    assert r.status_code == 303
    assert r.headers["location"].startswith("/admin/generate/statement/")


def test_an_empty_pasted_statement_is_refused(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "llm_help_available", True)
    r = client.post("/admin/generate/from-statement", data={"statement": "   "})
    assert r.status_code == 400
    assert "Paste a problem statement" in r.text


def test_an_unknown_statement_id_does_not_500(client, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "llm_help_available", True)
    r = client.get("/admin/generate/statement/nope-not-a-real-id",
                   follow_redirects=False)
    assert r.status_code in (303, 404)


def test_an_unknown_draft_id_does_not_500(client):
    r = client.get("/admin/generate/review/nope-not-a-real-id",
                   follow_redirects=False)
    assert r.status_code in (303, 404)


def test_generate_review_index_renders(client):
    r = client.get("/admin/generate/review", follow_redirects=False)
    assert r.status_code in (200, 303)
