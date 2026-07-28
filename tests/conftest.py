"""Shared pytest setup.

**The first thing this file does is redirect the database**, and it has to be
the first thing: ``app.config.Settings.DB_PATH`` reads ``LOOTCODE_DB`` at *class
definition* time, so the value is fixed the moment anything imports ``app.*``.
pytest imports every conftest before it imports a test module, which makes this
the only place the redirect can happen.

Before this existed, ``TestClient(app)`` ran the real lifespan against the
developer's live ``lootcode.db``: ``test_accounts.py`` created real users and
submissions in it and nothing ever removed them, and ``test_app.py`` mutated the
``Collection`` table. ``test_jsontext_bigint.py`` was the one module that got it
right, with its own temp engine.

Everything else here is the fixtures the test modules used to each declare for
themselves.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

_TMP_DIR = Path(tempfile.mkdtemp(prefix="lootcode-tests-"))
os.environ["LOOTCODE_DB"] = str(_TMP_DIR / "test.db")

# ruff: noqa: E402 - every import below must follow the redirect above.
import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app

#: Where the live developer database sits. Nothing in the suite may touch it.
_REAL_DB = Path(__file__).resolve().parent.parent / "lootcode.db"


def pytest_configure(config) -> None:
    """Fail the run outright if the redirect above did not take.

    A cheap assertion, but the failure it guards against is expensive and
    silent: a test suite quietly writing into the real bank.
    """
    if Path(settings.DB_PATH).resolve() == _REAL_DB.resolve():
        raise pytest.UsageError(
            f"tests are pointed at the live database ({_REAL_DB}). "
            "Something imported app.config before tests/conftest.py ran."
        )


def pytest_unconfigure(config) -> None:
    shutil.rmtree(_TMP_DIR, ignore_errors=True)


@pytest.fixture(scope="session")
def client() -> TestClient:
    """The app, started for real.

    Session-scoped because entering the context manager runs the lifespan —
    ``init_db`` plus a full seed of the bank from ``content/`` — and there is no
    reason to pay for that per module. Was declared three times, identically, in
    test_app / test_assets / test_accounts.
    """
    with TestClient(app) as c:
        yield c


@pytest.fixture
def new_browser():
    """Factory for an extra client with its own cookie jar — a "second browser".

    Deliberately *not* used as a context manager: entering one re-runs the
    lifespan, and the app has already been started (and the bank seeded) by the
    session-scoped ``client``. These clients only need a separate cookie jar.
    """
    return lambda: TestClient(app)


@pytest.fixture
def db():
    """A session against the temp database, closed afterwards."""
    from app.db import SessionLocal

    with SessionLocal() as session:
        yield session


@pytest.fixture
def tmp_content_dir(tmp_path, monkeypatch):
    """An empty problem root, swapped in for ``settings.CONTENT_DIR``.

    For tests that write problems to disk (``app.content``) without touching the
    real bank. ``content_dirs`` is a property over CONTENT_DIR and
    EXTENDED_CONTENT_DIR, so both are redirected.
    """
    root = tmp_path / "problems"
    root.mkdir()
    extended = tmp_path / "problems-extended"
    extended.mkdir()
    monkeypatch.setattr(settings, "CONTENT_DIR", root)
    monkeypatch.setattr(settings, "EXTENDED_CONTENT_DIR", extended)
    return root
