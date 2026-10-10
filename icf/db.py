"""ICF's own SQLite database: engine, session factory, schema creation.

Separate from ``lootcode.db`` on purpose. That file holds accounts, submissions
and solved history that exist nowhere else, and this is an *optional* feature:
adding tables to it — and orphaning them the day the folder is deleted — is the
coupling this extension is built to avoid. Rows here reference a user by the id
in the core ``lc_uid`` cookie, with no cross-file foreign key.

The engine is created lazily, so merely importing the extension (which happens
at startup, before anyone has visited ``/icf``) does not create a database file.
Same pragmas as core: WAL, a busy timeout, foreign keys on.
"""
from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

_engine: Engine | None = None
_sessionmaker: sessionmaker | None = None


class Base(DeclarativeBase):
    """A metadata of its own — core's ``create_all`` must not see these tables,
    and ours must not create core's."""


def _apply_pragmas(dbapi_connection, _record) -> None:
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
    finally:
        cursor.close()


def engine() -> Engine:
    """The engine, created (and the schema ensured) on first use."""
    global _engine, _sessionmaker
    if _engine is None:
        Path(settings.DB_PATH).parent.mkdir(parents=True, exist_ok=True)
        _engine = create_engine(settings.DATABASE_URL,
                                connect_args={"check_same_thread": False},
                                future=True)
        event.listen(_engine, "connect", _apply_pragmas)
        _sessionmaker = sessionmaker(bind=_engine, autoflush=False,
                                     expire_on_commit=False)
        from . import models  # noqa: F401 - register the tables on Base

        Base.metadata.create_all(bind=_engine)
    return _engine


def SessionLocal() -> Session:  # noqa: N802 - mirrors app.db's spelling
    engine()  # ensures _sessionmaker
    if _sessionmaker is None:  # pragma: no cover - engine() always sets it
        raise RuntimeError("ICF database is not initialised")
    return _sessionmaker()


@contextmanager
def session() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db() -> Iterator[Session]:
    """FastAPI dependency, mirroring ``app.db.get_db``."""
    with session() as db:
        yield db


def reset_for_tests() -> None:
    """Drop the cached engine so a test can point ICF_DB somewhere else."""
    global _engine, _sessionmaker
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _sessionmaker = None
