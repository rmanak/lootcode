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
        if "hints" not in cols:
            # JSON list of up to 3 hint strings; NULL on existing rows until the
            # next seed upserts them (the template treats NULL/empty as "no hints").
            conn.exec_driver_sql("ALTER TABLE problems ADD COLUMN hints JSON")

        # Class-based "design" problems (see specs/problem-schema.md). Existing
        # rows default to the single-function contract; the next content re-seed
        # fills class_name/class_methods for any kind="class" problem.
        if "kind" not in cols:
            conn.exec_driver_sql(
                "ALTER TABLE problems ADD COLUMN kind VARCHAR "
                "NOT NULL DEFAULT 'function'")
        if "class_name" not in cols:
            conn.exec_driver_sql("ALTER TABLE problems ADD COLUMN class_name VARCHAR")
        if "class_methods" not in cols:
            conn.exec_driver_sql("ALTER TABLE problems ADD COLUMN class_methods JSON")

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

        # Fix SQLite NUMERIC affinity on the test-case JSON columns. A column
        # declared JSON gets NUMERIC affinity, so a bare big-integer JSON payload
        # (> 2**63) is coerced to a lossy float on insert (a huge exact answer
        # becomes e.g. 4.697e+52 and then mis-grades a correct solution). Rebuild
        # test_cases with TEXT-affinity columns (matching models.JSONText) so JSON
        # is stored verbatim. Existing rows are copied so a restart never sees an
        # empty suite; any value that was already corrupted is restored by the next
        # content re-seed (scripts/seed.py). Detected by the old declared type, so
        # this runs once. SQLite can't ALTER a column's type, hence the rebuild.
        tcols = {row[1]: (row[2] or "") for row in conn.exec_driver_sql(
            "PRAGMA table_info(test_cases)").fetchall()}
        if tcols and tcols.get("expected", "").upper() == "JSON":
            conn.exec_driver_sql("ALTER TABLE test_cases RENAME TO _test_cases_old")
            conn.exec_driver_sql(
                "CREATE TABLE test_cases ("
                " id INTEGER NOT NULL,"
                " problem_id INTEGER NOT NULL,"
                " name VARCHAR NOT NULL,"
                " input TEXT NOT NULL,"
                " expected TEXT NOT NULL,"
                " weight INTEGER NOT NULL,"
                " hidden BOOLEAN NOT NULL,"
                " PRIMARY KEY (id),"
                " FOREIGN KEY(problem_id) REFERENCES problems (id))")
            conn.exec_driver_sql(
                "INSERT INTO test_cases"
                " (id, problem_id, name, input, expected, weight, hidden)"
                " SELECT id, problem_id, name, input, expected, weight, hidden"
                " FROM _test_cases_old")
            conn.exec_driver_sql("DROP TABLE _test_cases_old")
