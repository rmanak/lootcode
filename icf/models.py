"""ICF's ORM models: attempts, per-level state, runs and their cases.

An **attempt** is one sitting at one problem: a clock, four levels that unlock
in order, and every run made against it. Problems themselves are *not* here —
they are read from disk (see ``icf/content.py``).
"""
from __future__ import annotations

import uuid
from datetime import UTC, datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

#: An attempt is live, ended by the solver, or out of time.
ACTIVE, FINISHED, EXPIRED = "active", "finished", "expired"
#: Exam attempts run against the clock; practice attempts have no expiry.
EXAM, PRACTICE = "exam", "practice"


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(UTC)


class Attempt(Base):
    __tablename__ = "icf_attempts"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    #: The core cookie identity (`users.id` in lootcode.db). Deliberately not a
    #: foreign key — the two databases are independent files.
    user_id: Mapped[str] = mapped_column(String, index=True)
    slug: Mapped[str] = mapped_column(String, index=True)
    mode: Mapped[str] = mapped_column(String, default=EXAM)
    status: Mapped[str] = mapped_column(String, default=ACTIVE)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=_now)
    #: NULL for practice attempts: no clock, no expiry.
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    highest_level_passed: Mapped[int] = mapped_column(Integer, default=0)

    levels: Mapped[list[LevelState]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan",
        order_by="LevelState.level")
    runs: Mapped[list[Run]] = relationship(
        back_populates="attempt", cascade="all, delete-orphan",
        order_by="Run.created_at")
    draft: Mapped[Draft | None] = relationship(
        back_populates="attempt", cascade="all, delete-orphan", uselist=False)


class LevelState(Base):
    __tablename__ = "icf_level_state"
    __table_args__ = (UniqueConstraint("attempt_id", "level"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("icf_attempts.id", ondelete="CASCADE"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    unlocked_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    passed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    best_passed: Mapped[int] = mapped_column(Integer, default=0)
    best_total: Mapped[int] = mapped_column(Integer, default=0)

    attempt: Mapped[Attempt] = relationship(back_populates="levels")

    @property
    def unlocked(self) -> bool:
        return self.unlocked_at is not None

    @property
    def passed(self) -> bool:
        return self.passed_at is not None


class Run(Base):
    __tablename__ = "icf_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("icf_attempts.id", ondelete="CASCADE"), index=True)
    #: The level the solver aimed at. A submit also re-runs 1…level-1.
    level: Mapped[int] = mapped_column(Integer)
    #: "run" = visible cases for this level only; "submit" = everything up to it.
    mode: Mapped[str] = mapped_column(String, default="run")
    code: Mapped[str] = mapped_column(Text, default="")
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    all_passed: Mapped[bool] = mapped_column(Boolean, default=False)
    runtime_ms: Mapped[float] = mapped_column(Float, default=0.0)
    #: Made after the clock ran out: recorded and shown, but it never unlocks.
    late: Mapped[bool] = mapped_column(Boolean, default=False)
    load_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)

    attempt: Mapped[Attempt] = relationship(back_populates="runs")
    cases: Mapped[list[RunCase]] = relationship(
        back_populates="run", cascade="all, delete-orphan", order_by="RunCase.id")


class RunCase(Base):
    __tablename__ = "icf_run_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_id: Mapped[str] = mapped_column(
        ForeignKey("icf_runs.id", ondelete="CASCADE"), index=True)
    level: Mapped[int] = mapped_column(Integer)
    func: Mapped[str] = mapped_column(String)
    label: Mapped[str] = mapped_column(String, default="")
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String)     # passed|failed|timeout|error
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_ms: Mapped[float] = mapped_column(Float, default=0.0)
    stdout: Mapped[str] = mapped_column(Text, default="")

    run: Mapped[Run] = relationship(back_populates="cases")


class Draft(Base):
    """The editor buffer for an attempt, autosaved so a reload loses nothing."""

    __tablename__ = "icf_drafts"

    attempt_id: Mapped[str] = mapped_column(
        ForeignKey("icf_attempts.id", ondelete="CASCADE"), primary_key=True)
    code: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=_now,
                                                 onupdate=_now)

    attempt: Mapped[Attempt] = relationship(back_populates="draft")
