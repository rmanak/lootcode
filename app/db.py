"""Database engine, session factory, and the FastAPI session dependency."""
from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite + threaded server
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables. Imports models so they register on the metadata."""
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _migrate()


def _migrate() -> None:
    """Tiny additive migrations for an existing SQLite DB (no Alembic for V1)."""
    with engine.begin() as conn:
        cols = {row[1] for row in conn.exec_driver_sql(
            "PRAGMA table_info(problems)").fetchall()}
        if "compare" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE problems ADD COLUMN compare VARCHAR "
                "NOT NULL DEFAULT 'exact'")

        # V2 optional accounts: add nullable auth columns to an existing users
        # table. SQLite forbids adding a UNIQUE column via ALTER, so the columns
        # go in plain and uniqueness is enforced by separate indexes below.
        ucols = {row[1] for row in conn.exec_driver_sql(
            "PRAGMA table_info(users)").fetchall()}
        for name, ddl in (
            ("username", "ALTER TABLE users ADD COLUMN username VARCHAR"),
            ("email", "ALTER TABLE users ADD COLUMN email VARCHAR"),
            ("password_hash", "ALTER TABLE users ADD COLUMN password_hash VARCHAR"),
            ("claimed_at", "ALTER TABLE users ADD COLUMN claimed_at DATETIME"),
            ("last_login_at", "ALTER TABLE users ADD COLUMN last_login_at DATETIME"),
        ):
            if name not in ucols:
                conn.exec_driver_sql(ddl)
        # NULLs are exempt from UNIQUE in SQLite, so guests (all NULL) don't clash.
        conn.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_username ON users(username)")
        conn.exec_driver_sql(
            "CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users(email)")
