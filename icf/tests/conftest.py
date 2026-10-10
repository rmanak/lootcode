"""Fixtures for the ICF suite.

The database is already redirected by the repo-root ``conftest.py`` (ICF_DB →
a temp file), which has to happen before ``icf.config`` is imported.

Most tests run against a **toy** problem generated into a temp directory
rather than against the shipped bank: four levels with one visible and one
hidden case each, so a full submit costs a handful of sandbox cases instead of
fifty-seven. The shipped problems are covered by
``icf/scripts/verify_icf.py`` and by ``test_problems.py``.
"""
from __future__ import annotations

import json
import shutil
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app
from icf import content
from icf.config import settings

TOY_SLUG = "toy-counter"

_STARTER = '''class Counter:
    def __init__(self):
        pass

    def add(self, n):
        pass

    def total(self):
        pass

    def undo(self):
        pass

    def label(self):
        pass
'''

_CANONICAL = '''class Counter:
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

_CASES = {
    (1, "visible"): [("add_returns_count", "add returns how many values there are",
                      "c = Counter()\n    expect(c.add(2), 1)\n    expect(c.add(3), 2)")],
    (1, "hidden"): [("add_many", "adding many values keeps counting",
                     "c = Counter()\n    for i in range(5):\n        expect(c.add(i), i + 1)")],
    (2, "visible"): [("total_sums", "total sums everything added",
                      "c = Counter()\n    c.add(2)\n    c.add(5)\n    expect(c.total(), 7)")],
    (2, "hidden"): [("total_empty", "an empty counter totals zero",
                     "expect(Counter().total(), 0)")],
    (3, "visible"): [("undo_removes", "undo drops the last value",
                      "c = Counter()\n    c.add(2)\n    c.add(5)\n    expect(c.undo(), True)"
                      "\n    expect(c.total(), 2)")],
    (3, "hidden"): [("undo_empty", "undo on an empty counter reports False",
                     "expect(Counter().undo(), False)")],
    (4, "visible"): [("label_joins", "label joins the values with +",
                      "c = Counter()\n    c.add(1)\n    c.add(2)\n    expect(c.label(), '1+2')")],
    (4, "hidden"): [("label_empty", "an empty counter labels as an empty string",
                     "expect(Counter().label(), '')")],
}

_METHODS = {
    1: ["def add(self, n) -> int: ..."],
    2: ["def total(self) -> int: ..."],
    3: ["def undo(self) -> bool: ..."],
    4: ["def label(self) -> str: ..."],
}


def write_toy_problem(root: Path, slug: str = TOY_SLUG) -> Path:
    """Create a complete, valid four-level problem under ``root/slug``."""
    directory = root / slug
    (directory / "levels").mkdir(parents=True, exist_ok=True)
    (directory / "starter").mkdir(exist_ok=True)
    (directory / "solution").mkdir(exist_ok=True)
    (directory / "meta.json").write_text(json.dumps({
        "slug": slug,
        "title": "Toy Counter",
        "difficulty": "easy",
        "blurb": "A counter, in four small steps.",
        "class_name": "Counter",
        "time_cap_minutes": 90,
        "case_time_limit_ms": 3000,
        "levels": [{"level": n, "title": f"Level {n}", "points": 25,
                    "methods": _METHODS[n]} for n in (1, 2, 3, 4)],
    }), encoding="utf-8")
    (directory / "problem.md").write_text("Implement a counter.\n", encoding="utf-8")
    for n in (1, 2, 3, 4):
        (directory / "levels" / f"level{n}.md").write_text(
            f"Level {n} asks for one more method.\n", encoding="utf-8")
    (directory / "starter" / "solution.py").write_text(_STARTER, encoding="utf-8")
    (directory / "solution" / "solution.py").write_text(_CANONICAL, encoding="utf-8")

    for (level, visibility), cases in _CASES.items():
        target = directory / "tests" / f"level{level}"
        target.mkdir(parents=True, exist_ok=True)
        body = ["from icf_testkit import case, expect", ""]
        for func, label, code in cases:
            body += [f'@case("{label}")', f"def {func}(Counter):", f"    {code}", ""]
        (target / f"{visibility}.py").write_text("\n".join(body), encoding="utf-8")
    return directory


@pytest.fixture
def toy_root(tmp_path, monkeypatch) -> Iterator[Path]:
    """A problems directory holding just the toy problem, swapped in globally."""
    root = tmp_path / "problems"
    root.mkdir()
    write_toy_problem(root)
    monkeypatch.setattr(settings, "PROBLEMS_DIR", root)
    content.clear_cache()
    yield root
    content.clear_cache()


@pytest.fixture
def toy(toy_root):
    problem = content.load(TOY_SLUG)
    assert problem is not None
    return problem


@pytest.fixture
def icf_client(toy_root) -> TestClient:
    """A client with its own cookie jar, served the toy problem."""
    return TestClient(app)


@pytest.fixture(scope="session", autouse=True)
def _core_schema():
    """Create core's tables in the redirected test database.

    ICF pages are served by the core app, whose identity middleware writes a
    `users` row — so the core schema has to exist even though nothing here
    touches the problem bank. Core's own suite gets this from the lifespan
    (which also seeds 1,100 problems); this is the cheap half of it.
    """
    from app.db import init_db

    init_db()


@pytest.fixture
def new_browser():
    """Factory for a client with a fresh cookie jar — a second visitor."""
    return lambda: TestClient(app)


@pytest.fixture(autouse=True)
def _clean_icf_db():
    """Each test starts with an empty attempt store."""
    from icf.db import Base, engine

    yield
    with engine().begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.exec_driver_sql(f"DELETE FROM {table.name}")


def pytest_sessionfinish(session, exitstatus) -> None:
    shutil.rmtree(Path(__file__).resolve().parent / "__pycache__", ignore_errors=True)
