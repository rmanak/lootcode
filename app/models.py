"""SQLAlchemy ORM models. See docs/data-model.md."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Optional account (V2). A row is an anonymous *guest* while these are NULL;
    # setting username + password_hash "claims" it into an account. See
    # docs/user-accounts-v2.md. NULLs are exempt from the UNIQUE indexes in
    # SQLite, so every guest can share NULL username/email.
    username: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True)
    email: Mapped[str | None] = mapped_column(
        String, unique=True, index=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    claimed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    submissions: Mapped[list["Submission"]] = relationship(back_populates="user")

    @property
    def is_account(self) -> bool:
        """True once the guest row has been claimed with login credentials."""
        return self.password_hash is not None


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    difficulty: Mapped[str] = mapped_column(String, index=True)  # easy|medium|hard
    topics: Mapped[list] = mapped_column(JSON, default=list)
    statement_md: Mapped[str] = mapped_column(Text)

    # Function the harness calls (see specs/problem-schema.md)
    function_name: Mapped[str] = mapped_column(String)
    params: Mapped[list] = mapped_column(JSON, default=list)  # [{name,type}]
    return_type: Mapped[str] = mapped_column(String, default="")

    time_limit_ms: Mapped[int] = mapped_column(Integer, default=10_000)
    memory_limit_mb: Mapped[int] = mapped_column(Integer, default=512)
    scoring_type: Mapped[str] = mapped_column(String, default="weighted")
    points: Mapped[int] = mapped_column(Integer, default=100)
    # How the judge compares the returned value to `expected`:
    #   exact         — structural equality (default; order is significant)
    #   unordered     — the returned list is a multiset (top-level order ignored)
    #   set_of_lists  — list of lists; outer order AND each inner list's order ignored
    compare: Mapped[str] = mapped_column(String, default="exact")

    starter_code: Mapped[str] = mapped_column(Text, default="")
    # Reference solution that passes all tests. Never exposed to solvers.
    canonical_solution: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str] = mapped_column(String, default="file")  # file|manual|ai
    is_published: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    tests: Mapped[list["TestCase"]] = relationship(
        back_populates="problem", cascade="all, delete-orphan", order_by="TestCase.id"
    )


class Collection(Base):
    """A curated, **system-defined** list of problems (e.g. "Blind 73").

    Membership and study order live in `content/collections/<slug>.json` and are
    seeded into the DB on startup (see `store.seed_collections`). There are no
    user-defined collections — these ship with the app. See docs/collections.md."""
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[str] = mapped_column(String)
    subtitle: Mapped[str] = mapped_column(String, default="")
    source: Mapped[str] = mapped_column(String, default="file")  # file (only, for now)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)

    # Ordered by the curated study position, not problem id.
    items: Mapped[list["CollectionProblem"]] = relationship(
        back_populates="collection", cascade="all, delete-orphan",
        order_by="CollectionProblem.position",
    )


class CollectionProblem(Base):
    """One problem's membership in one collection, carrying its study-order
    `position` (the order it appears in the manifest)."""
    __tablename__ = "collection_problems"
    __table_args__ = (
        UniqueConstraint("collection_id", "problem_id", name="uq_collection_problem"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    collection_id: Mapped[int] = mapped_column(ForeignKey("collections.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    position: Mapped[int] = mapped_column(Integer, default=0)

    collection: Mapped[Collection] = relationship(back_populates="items")
    problem: Mapped[Problem] = relationship()


class TestCase(Base):
    __tablename__ = "test_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"))
    name: Mapped[str] = mapped_column(String)
    input: Mapped[dict] = mapped_column(JSON)       # {param_name: value}
    expected: Mapped[object] = mapped_column(JSON)  # any JSON value
    weight: Mapped[int] = mapped_column(Integer, default=1)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)

    problem: Mapped[Problem] = relationship(back_populates="tests")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    code: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="done")
    score: Mapped[int] = mapped_column(Integer, default=0)
    passed_count: Mapped[int] = mapped_column(Integer, default=0)
    total_count: Mapped[int] = mapped_column(Integer, default=0)
    runtime_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now, index=True)

    user: Mapped[User] = relationship(back_populates="submissions")
    problem: Mapped[Problem] = relationship()
    results: Mapped[list["TestResult"]] = relationship(
        back_populates="submission", cascade="all, delete-orphan"
    )

    @property
    def solved(self) -> bool:
        return self.total_count > 0 and self.passed_count == self.total_count


class KnownProblem(Base):
    """A user has marked a problem as "known" — they already know the solution and
    don't want it surfaced when browsing for new work. Independent of `solved`
    (derived from Submissions): a problem can be known without ever being solved.
    Solved problems are treated as *implicitly* known in the UI's "unknown only"
    filter, but that's a presentation rule — it isn't recorded here."""
    __tablename__ = "known_problems"
    __table_args__ = (
        UniqueConstraint("user_id", "problem_id", name="uq_known_user_problem"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problems.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=_now)


class TestResult(Base):
    __tablename__ = "test_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    submission_id: Mapped[str] = mapped_column(ForeignKey("submissions.id"))
    name: Mapped[str] = mapped_column(String)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String)  # passed|wrong|timeout|error
    time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)

    submission: Mapped[Submission] = relationship(back_populates="results")
