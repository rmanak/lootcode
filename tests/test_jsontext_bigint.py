"""Regression: big-integer JSON test values survive the DB round-trip exactly.

A column whose declared type is ``JSON`` gets NUMERIC affinity in SQLite, which
silently coerces a bare integer larger than 2**63 into a lossy float on insert
(e.g. an exact answer ``4697…0`` comes back as ``4.697e+52`` and mis-grades a
correct solution). ``TestCase.input``/``expected`` use ``models.JSONText`` (TEXT
affinity) so the serialized JSON is stored verbatim. See app/models.JSONText and
the rebuild migration in app/db._migrate.
"""
import os
import tempfile

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.db import Base
from app.models import Problem
from app.models import TestCase as TestCaseModel

BIG = 46970481301346070551168882056905936076800000000000000  # >> 2**63


@pytest.fixture
def session():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    engine = create_engine(f"sqlite:///{path}")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as s:
            yield s
    finally:
        engine.dispose()
        os.unlink(path)


def test_big_integer_roundtrips_exact(session):
    prob = Problem(slug="t-big", title="t", difficulty="easy",
                   statement_md="", function_name="f")
    session.add(prob)
    session.flush()
    session.add(TestCaseModel(problem_id=prob.id, name="c1",
                         input={"n": BIG}, expected=BIG, weight=1, hidden=False))
    session.commit()
    session.expire_all()  # drop cached instances so we read back through the DB

    t = session.scalar(select(TestCaseModel))
    assert t.expected == BIG and isinstance(t.expected, int)
    assert t.input["n"] == BIG and isinstance(t.input["n"], int)

    # And it is physically stored as verbatim TEXT, not a coerced float.
    raw = session.connection().exec_driver_sql(
        "SELECT expected FROM test_cases").scalar()
    assert raw == str(BIG)


def test_fresh_schema_uses_text_affinity(session):
    ddl = session.connection().exec_driver_sql(
        "SELECT sql FROM sqlite_master WHERE name='test_cases'").scalar()
    assert "input TEXT" in ddl and "expected TEXT" in ddl
