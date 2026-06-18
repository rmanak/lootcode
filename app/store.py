"""Database operations on top of the models: upsert problems, seed, progress."""
from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import auth, content
from .models import KnownProblem, Problem, Submission, TestCase, User
from .tags import normalize_tags


def _now() -> datetime:
    return datetime.now(timezone.utc)

_PROBLEM_FIELDS = (
    "title", "difficulty", "topics", "statement_md", "function_name", "params",
    "return_type", "time_limit_ms", "memory_limit_mb", "scoring_type", "points",
    "compare", "starter_code", "canonical_solution", "source",
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
    db.delete(guest)
    db.commit()
