"""Database operations on top of the models: upsert problems, seed, progress."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, content
from .models import (
    Collection,
    CollectionProblem,
    KnownProblem,
    Problem,
    Submission,
    TestCase,
    User,
    VisitLaterProblem,
)
from .tags import normalize_tags

log = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)

_PROBLEM_FIELDS = (
    "title", "difficulty", "topics", "hints", "statement_md", "function_name",
    "params", "return_type", "time_limit_ms", "memory_limit_mb", "scoring_type",
    "points", "compare", "starter_code", "canonical_solution", "source",
)


def upsert_problem(db: Session, data: dict) -> Problem:
    """Create or update a problem (and replace its tests) by slug."""
    prob = db.scalar(select(Problem).where(Problem.slug == data["slug"]))
    if prob is None:
        prob = Problem(slug=data["slug"])
        db.add(prob)
    for field in _PROBLEM_FIELDS:
        if field in data:
            setattr(prob, field, data[field])
    # Tags are stored only from the canonical vocabulary (see app/tags.py).
    prob.topics = normalize_tags(prob.topics)

    prob.tests.clear()
    db.flush()
    for t in data.get("tests", []):
        prob.tests.append(TestCase(
            name=t["name"], input=t["input"], expected=t["expected"],
            weight=t.get("weight", 1), hidden=t.get("hidden", False),
        ))
    db.commit()
    db.refresh(prob)
    return prob


def seed_from_content(db: Session) -> int:
    """Load every problem under content/problems/ into the database."""
    count = 0
    for data in content.load_all():
        upsert_problem(db, data)
        count += 1
    return count


def seed_collections(db: Session) -> tuple[int, list[str]]:
    """Seed curated problem lists from content/collections/*.json.

    Upserts each `Collection` by slug and rebuilds its membership rows, resolving
    every problem slug to a `Problem.id` in manifest order (the study order).
    Unknown slugs — a typo, or a problem not (yet) in the bank — are skipped and
    returned as "<collection>:<slug>" so a caller can surface them; they never
    crash seeding. Idempotent. Returns (collections_seeded, unresolved_slugs).

    Seeds problems first (`seed_from_content`) since membership needs problem ids.
    """
    problem_ids = {
        slug: pid for slug, pid in db.execute(select(Problem.slug, Problem.id)).all()
    }
    unresolved: list[str] = []
    count = 0
    for data in content.load_collections():
        coll = db.scalar(select(Collection).where(Collection.slug == data["slug"]))
        if coll is None:
            coll = Collection(slug=data["slug"])
            db.add(coll)
        coll.title = data["title"]
        coll.subtitle = data.get("subtitle", "")
        coll.source = "file"
        coll.items.clear()
        db.flush()
        position = 0
        for pslug in data["problems"]:
            pid = problem_ids.get(pslug)
            if pid is None:
                unresolved.append(f"{data['slug']}:{pslug}")
                continue
            coll.items.append(CollectionProblem(problem_id=pid, position=position))
            position += 1
        count += 1
    db.commit()
    if unresolved:
        log.warning("Collections reference %d unknown problem slug(s): %s",
                    len(unresolved), ", ".join(unresolved))
    return count, unresolved


def collection_member_ids(db: Session, slug: str) -> list[int]:
    """Ordered problem ids for a collection (study order), or [] if unknown."""
    coll = db.scalar(select(Collection).where(Collection.slug == slug))
    return [it.problem_id for it in coll.items] if coll else []


def user_solved_problem_ids(db: Session, user_id: str) -> set[int]:
    rows = db.execute(
        select(Submission.problem_id).where(
            Submission.user_id == user_id,
            Submission.total_count > 0,
            Submission.passed_count == Submission.total_count,
        )
    ).all()
    return {r[0] for r in rows}


def user_known_problem_ids(db: Session, user_id: str) -> set[int]:
    """Problems the user has explicitly marked "known". Solved problems are *not*
    folded in here — that implicit "solved ⇒ known" rule lives in the UI/filters
    (see the index route), so this set stays a faithful record of explicit marks."""
    rows = db.execute(
        select(KnownProblem.problem_id).where(KnownProblem.user_id == user_id)
    ).all()
    return {r[0] for r in rows}


def set_problem_known(db: Session, user_id: str, problem_id: int,
                      known: bool) -> bool:
    """Mark or unmark a problem as known for a user. Idempotent: marking an
    already-known problem (or unmarking an unknown one) is a no-op. Returns the
    resulting known state."""
    existing = db.scalar(select(KnownProblem).where(
        KnownProblem.user_id == user_id, KnownProblem.problem_id == problem_id))
    if known and existing is None:
        db.add(KnownProblem(user_id=user_id, problem_id=problem_id))
        db.commit()
    elif not known and existing is not None:
        db.delete(existing)
        db.commit()
    return known


def user_visit_later_problem_ids(db: Session, user_id: str) -> set[int]:
    """Problems the user has flagged "visit later". A pure record of explicit
    bookmarks — solved/known problems are never folded in, so the "Visit later"
    filter shows exactly what the user saved."""
    rows = db.execute(
        select(VisitLaterProblem.problem_id).where(
            VisitLaterProblem.user_id == user_id)
    ).all()
    return {r[0] for r in rows}


def set_problem_visit_later(db: Session, user_id: str, problem_id: int,
                            visit_later: bool) -> bool:
    """Flag or unflag a problem as "visit later" for a user. Idempotent: flagging
    an already-flagged problem (or unflagging one that isn't) is a no-op. Returns
    the resulting state."""
    existing = db.scalar(select(VisitLaterProblem).where(
        VisitLaterProblem.user_id == user_id,
        VisitLaterProblem.problem_id == problem_id))
    if visit_later and existing is None:
        db.add(VisitLaterProblem(user_id=user_id, problem_id=problem_id))
        db.commit()
    elif not visit_later and existing is not None:
        db.delete(existing)
        db.commit()
    return visit_later


# --- Optional accounts (V2). See docs/user-accounts-v2.md. -------------------
# All raise ValueError (with a user-facing message) on bad input so routes can
# surface a single error string. A guest = a User row with no password_hash.

def create_account(db: Session, user_id: str, username: str, password: str,
                   email: str | None = None) -> User:
    """Claim the *current* guest row as an account, in place. Lossless by design:
    the caller's submissions already live on this row, so there's nothing to
    migrate. Raises ValueError if the row is already an account, or the
    username/email is taken or invalid."""
    username = auth.validate_username(username)
    email = auth.validate_email(email)
    auth.validate_password(password)

    user = db.get(User, user_id)
    if user is None:
        raise ValueError("Your session expired — reload the page and try again.")
    if user.is_account:
        raise ValueError("You're already signed in to an account.")
    if db.scalar(select(User).where(User.username == username)):
        raise ValueError("That username is taken.")
    if email and db.scalar(select(User).where(User.email == email)):
        raise ValueError("That email is already in use.")

    user.username = username
    user.email = email
    user.password_hash = auth.hash_password(password)
    user.claimed_at = user.last_login_at = _now()
    if not user.name or user.name == "guest":
        user.name = username
    try:
        db.commit()
    except IntegrityError:  # lost a uniqueness race between the check and commit
        db.rollback()
        raise ValueError("That username or email is already in use.")
    db.refresh(user)
    return user


def authenticate(db: Session, username: str, password: str) -> User | None:
    """Return the account for valid credentials (and stamp last_login_at), else None."""
    username = auth.normalize_username(username)
    if not username:
        return None
    user = db.scalar(select(User).where(User.username == username))
    if user and auth.verify_password(password, user.password_hash):
        user.last_login_at = _now()
        db.commit()
        return user
    return None


def merge_user(db: Session, from_id: str, into_id: str) -> None:
    """Fold an unclaimed guest's submissions into an account, then delete the
    guest row. No-op when the ids match or `from_id` isn't an unclaimed guest —
    we never reassign one account's data into another."""
    if from_id == into_id:
        return
    guest = db.get(User, from_id)
    if guest is None or guest.is_account:
        return
    db.execute(update(Submission).where(Submission.user_id == from_id)
               .values(user_id=into_id))
    # Move the guest's "known" marks too, skipping any the account already has
    # (the (user_id, problem_id) uniqueness constraint would otherwise trip).
    account_known = user_known_problem_ids(db, into_id)
    for mark in db.scalars(select(KnownProblem).where(
            KnownProblem.user_id == from_id)):
        if mark.problem_id in account_known:
            db.delete(mark)
        else:
            mark.user_id = into_id
    # Same for the guest's "visit later" bookmarks.
    account_later = user_visit_later_problem_ids(db, into_id)
    for mark in db.scalars(select(VisitLaterProblem).where(
            VisitLaterProblem.user_id == from_id)):
        if mark.problem_id in account_later:
            db.delete(mark)
        else:
            mark.user_id = into_id
    db.delete(guest)
    db.commit()
