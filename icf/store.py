"""Attempt lifecycle: start, grade, unlock, autosave, finish.

Everything that decides *state* lives here rather than in the routers, because
the rules — which level is unlocked, what a late run counts for, when an
attempt expires — are the feature, and they need to be testable without HTTP.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from .content import LEVELS, Problem
from .models import (
    ACTIVE,
    EXAM,
    EXPIRED,
    FINISHED,
    PRACTICE,
    Attempt,
    Draft,
    LevelState,
    Run,
    RunCase,
)
from .runner import GradedRun


def _now() -> datetime:
    return datetime.now(UTC)


def _aware(dt: datetime | None) -> datetime | None:
    """SQLite hands back naive datetimes; every comparison here is in UTC."""
    if dt is None:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=UTC)


# --- attempts --------------------------------------------------------------

def start_attempt(db: Session, user_id: str, problem: Problem,
                  mode: str = EXAM) -> Attempt:
    """Begin a sitting. Level 1 is unlocked immediately; 2–4 are not."""
    mode = PRACTICE if mode == PRACTICE else EXAM
    started = _now()
    attempt = Attempt(
        user_id=user_id, slug=problem.slug, mode=mode, status=ACTIVE,
        started_at=started,
        expires_at=(started + timedelta(minutes=problem.time_cap_minutes)
                    if mode == EXAM else None),
    )
    for number in LEVELS:
        attempt.levels.append(LevelState(
            level=number, unlocked_at=started if number == 1 else None))
    attempt.draft = Draft(code=problem.starter_code)
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    return attempt


def active_attempt(db: Session, user_id: str, slug: str) -> Attempt | None:
    """The solver's live attempt at this problem, if any. Expires it first, so
    an abandoned exam doesn't come back to life a day later."""
    attempt = db.scalar(
        select(Attempt)
        .where(Attempt.user_id == user_id, Attempt.slug == slug,
               Attempt.status == ACTIVE)
        .order_by(Attempt.started_at.desc()))
    if attempt is None:
        return None
    expire_if_due(db, attempt)
    return attempt


def get_attempt(db: Session, attempt_id: str, user_id: str) -> Attempt | None:
    """One attempt, only for the person who owns it."""
    attempt = db.get(Attempt, attempt_id)
    if attempt is None or attempt.user_id != user_id:
        return None
    expire_if_due(db, attempt)
    return attempt


def user_attempts(db: Session, user_id: str, slug: str | None = None,
                  limit: int = 50) -> list[Attempt]:
    stmt = select(Attempt).where(Attempt.user_id == user_id)
    if slug:
        stmt = stmt.where(Attempt.slug == slug)
    return list(db.scalars(stmt.order_by(Attempt.started_at.desc()).limit(limit)))


def remaining_ms(attempt: Attempt) -> int | None:
    """Milliseconds left on the clock, floored at 0. ``None`` in practice mode."""
    expires = _aware(attempt.expires_at)
    if expires is None:
        return None
    return max(0, int((expires - _now()).total_seconds() * 1000))


def expire_if_due(db: Session, attempt: Attempt) -> bool:
    """Flip a live exam attempt to ``expired`` once its clock runs out."""
    if attempt.status != ACTIVE or attempt.mode != EXAM:
        return False
    if remaining_ms(attempt) != 0:
        return False
    attempt.status = EXPIRED
    attempt.ended_at = _now()
    db.commit()
    return True


def finish_attempt(db: Session, attempt: Attempt) -> Attempt:
    if attempt.status == ACTIVE:
        attempt.status = FINISHED
        attempt.ended_at = _now()
        db.commit()
    return attempt


def elapsed_seconds(attempt: Attempt) -> int:
    end = _aware(attempt.ended_at) or _now()
    return max(0, int((end - (_aware(attempt.started_at) or end)).total_seconds()))


# --- level state -----------------------------------------------------------

def level_state(attempt: Attempt, number: int) -> LevelState | None:
    for state in attempt.levels:
        if state.level == number:
            return state
    return None


def is_unlocked(attempt: Attempt, number: int) -> bool:
    state = level_state(attempt, number)
    return bool(state and state.unlocked)


def highest_unlocked(attempt: Attempt) -> int:
    return max((s.level for s in attempt.levels if s.unlocked), default=1)


# --- runs ------------------------------------------------------------------

@dataclass(frozen=True)
class RunOutcome:
    """What a graded run did to the attempt, for the API to report."""

    run: Run
    graded: GradedRun
    late: bool
    unlocked_level: int | None   # the level this run just opened, if any


def _save_cases(db: Session, run: Run, graded: GradedRun) -> None:
    """Persist one run's cases.

    A hidden case is stored with no message and no output — the runner has
    already dropped both, and storing them anyway would leave the redaction
    one careless template away from being undone.
    """
    for lv in graded.levels:
        for c in lv.cases:
            db.add(RunCase(
                run_id=run.id, level=c.level, func=c.func, label=c.label,
                hidden=c.hidden, status=c.status,
                message=None if c.hidden else c.message,
                time_ms=c.time_ms, stdout="" if c.hidden else c.stdout))


def record_run(db: Session, attempt: Attempt, problem: Problem, level: int,
               mode: str, code: str, graded: GradedRun) -> RunOutcome:
    """Persist a graded run and apply it to the attempt's level state.

    Only a **submit** moves the attempt forward. A *run* is the fast feedback
    loop — the current level's visible cases — and unlocking on it would hand
    the next level to someone who has not passed the hidden tests, which is
    exactly what the gate is for. A run made after the clock expired is stored
    and shown, but never unlocks either.

    Passing a level is sticky: a later regression shows in the results but does
    not re-lock what was already earned, because taking progress away
    mid-attempt punishes the refactor the format is asking for.
    """
    expire_if_due(db, attempt)
    late = attempt.status != ACTIVE

    run = Run(attempt_id=attempt.id, level=level, mode=mode, code=code,
              passed_count=graded.passed_count, total_count=graded.total_count,
              all_passed=graded.all_passed, runtime_ms=graded.runtime_ms,
              late=late, load_error=graded.load_error)
    db.add(run)
    db.flush()
    _save_cases(db, run, graded)

    unlocked: int | None = None
    if not late and mode == "submit":
        for lv in graded.levels:
            state = level_state(attempt, lv.level)
            if state is None:
                continue
            if lv.passed_count >= state.best_passed:
                state.best_passed = lv.passed_count
                state.best_total = lv.total_count
            if lv.all_passed and state.passed_at is None:
                state.passed_at = _now()
        # A level is earned only when it *and* everything under it pass in the
        # same run: level 3 passing while level 1 regressed is not level 3 done.
        earned = 0
        for number in LEVELS:
            state = level_state(attempt, number)
            if state and state.passed:
                earned = number
            else:
                break
        attempt.highest_level_passed = max(attempt.highest_level_passed, earned)
        nxt = earned + 1
        next_state = level_state(attempt, nxt) if nxt in LEVELS else None
        if next_state is not None and not next_state.unlocked:
            next_state.unlocked_at = _now()
            unlocked = nxt
        if earned == max(LEVELS) and attempt.status == ACTIVE:
            attempt.status = FINISHED
            attempt.ended_at = _now()

    db.commit()
    db.refresh(run)
    return RunOutcome(run=run, graded=graded, late=late, unlocked_level=unlocked)


# --- drafts ----------------------------------------------------------------

def save_draft(db: Session, attempt: Attempt, code: str) -> None:
    if attempt.draft is None:
        attempt.draft = Draft(code=code)
    else:
        attempt.draft.code = code
        attempt.draft.updated_at = _now()
    db.commit()


def current_code(attempt: Attempt, problem: Problem) -> str:
    """What the editor should open with: the autosaved buffer, else the starter."""
    if attempt.draft is not None and attempt.draft.code.strip():
        return attempt.draft.code
    return problem.starter_code
