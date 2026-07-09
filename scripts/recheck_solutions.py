#!/usr/bin/env python3
"""Re-grade users' accepted solutions against the *current* test suites.

Two operations on the existing database:

  1. ``users`` — list every user with basic activity stats (how many
     submissions, how many distinct problems attempted, how many solved, last
     activity).

  2. ``check <user>`` — for one user, take the **latest successful submission**
     of every problem they have solved and re-run that exact code against the
     tests that are in the DB *now*, using the same execution + grading path the
     app uses (:func:`app.executor.run_submission`). Reports how many still pass
     and, crucially, which ones have **regressed** — i.e. were accepted before
     but fail today because the test suite has since been strengthened. Nothing
     about the sandbox / executor / judge is re-implemented here.

Why this exists: after hardening a problem's hidden tests (the ``test-strengthener``
agent / ``scripts/oracle.py`` / ``scripts/strengthen_tests.py``), an old solution
that "passed here but had a bug" can now be caught. This sweeps your own accepted
solutions to find those gaps.

Test source: by default it grades against the tests **currently in the database**
(the runtime source of truth — what the live app would judge against). Pass
``--from-content`` to instead load the freshest tests straight from
``content/problems/<slug>/`` — i.e. grade "as if you had just re-seeded", handy
right after strengthening tests without running ``scripts/seed.py``. (User and
submission data always come from the DB regardless.)

Usage:
    python scripts/recheck_solutions.py users              # all active users + stats
    python scripts/recheck_solutions.py users --all        # include zero-submission guests
    python scripts/recheck_solutions.py check arman         # re-grade vs the DB's tests
    python scripts/recheck_solutions.py check arman --from-content  # vs the freshest on-disk tests
    python scripts/recheck_solutions.py check arman -v      # + per-failing-test detail
    python scripts/recheck_solutions.py check <user-id> -j 8   # 8 problems in parallel

A user can be named by username, display name, full id, or an id prefix.
Exit status of ``check`` is 0 only when every rechecked solution still passes.
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from sqlalchemy import func, select  # noqa: E402

from app import content  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.models import Problem, Submission, User  # noqa: E402


# ---------------------------------------------------------------------------
# Small ANSI color helper (auto-disabled when output is not a TTY). Mirrors
# scripts/verify_bank.py so the two tools read the same.
# ---------------------------------------------------------------------------
class Palette:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _wrap(self, code: str, s: str) -> str:
        return f"\033[{code}m{s}\033[0m" if self.enabled else s

    def green(self, s: str) -> str:
        return self._wrap("32", s)

    def red(self, s: str) -> str:
        return self._wrap("31", s)

    def yellow(self, s: str) -> str:
        return self._wrap("33", s)

    def dim(self, s: str) -> str:
        return self._wrap("2", s)

    def bold(self, s: str) -> str:
        return self._wrap("1", s)

    def cyan(self, s: str) -> str:
        return self._wrap("36", s)


def _pct(passed: int, total: int) -> int:
    return round(100 * passed / total) if total else 0


def _fmt_dt(dt) -> str:
    return dt.strftime("%Y-%m-%d %H:%M") if dt else "-"


def _user_label(u: User) -> str:
    """Human handle for a user: username if claimed, else display name."""
    if u.username:
        return u.username
    return u.name or "(unnamed)"


# ===========================================================================
# Operation 1: list users + stats
# ===========================================================================
@dataclass
class UserStats:
    user: User
    n_subs: int = 0
    n_attempted: int = 0        # distinct problems with any submission
    n_solved: int = 0           # distinct problems fully passed (at submit time)
    last_activity: object = None


def _solved_filter():
    """SQL predicate for a submission that passed every test when it ran."""
    return (Submission.total_count > 0,
            Submission.passed_count == Submission.total_count)


def gather_user_stats(db) -> list[UserStats]:
    """One aggregate pass per metric, joined in Python by user id."""
    users = db.scalars(select(User)).all()
    stats = {u.id: UserStats(user=u) for u in users}

    # total submissions + last activity, per user
    for uid, n, last in db.execute(
        select(Submission.user_id, func.count(Submission.id),
               func.max(Submission.created_at))
        .group_by(Submission.user_id)
    ).all():
        if uid in stats:
            stats[uid].n_subs = n
            stats[uid].last_activity = last

    # distinct problems attempted, per user
    for uid, n in db.execute(
        select(Submission.user_id, func.count(func.distinct(Submission.problem_id)))
        .group_by(Submission.user_id)
    ).all():
        if uid in stats:
            stats[uid].n_attempted = n

    # distinct problems solved, per user
    for uid, n in db.execute(
        select(Submission.user_id, func.count(func.distinct(Submission.problem_id)))
        .where(*_solved_filter())
        .group_by(Submission.user_id)
    ).all():
        if uid in stats:
            stats[uid].n_solved = n

    return list(stats.values())


def print_users(db, c: Palette, args) -> int:
    rows = gather_user_stats(db)
    if not args.all:
        rows = [r for r in rows if r.n_subs > 0]
    # Most active first: solved, then submissions, then recency.
    rows.sort(key=lambda r: (r.n_solved, r.n_subs,
                             r.last_activity or _EPOCH), reverse=True)

    if not rows:
        print("No users found." if args.all
              else "No users with submissions (try --all).")
        return 0

    header = (f"{'USER':<20} {'KIND':<7} {'ID':<12} {'SUBS':>5} "
              f"{'SOLVED':>7} {'ATTEMPT':>8}  {'LAST ACTIVITY':<16}")
    print(c.bold(header))
    print(c.dim("-" * len(header)))
    for r in rows:
        u = r.user
        label = _user_label(u)
        if len(label) > 19:
            label = label[:18] + "…"
        kind = "account" if u.is_account else "guest"
        solved = c.green(f"{r.n_solved:>7}") if r.n_solved else f"{r.n_solved:>7}"
        print(f"{label:<20} {kind:<7} {u.id[:12]:<12} {r.n_subs:>5} "
              f"{solved} {r.n_attempted:>8}  {_fmt_dt(r.last_activity):<16}")

    n_acct = sum(1 for r in rows if r.user.is_account)
    print(c.dim(f"\n{len(rows)} user(s)  ({n_acct} account(s), "
                f"{len(rows) - n_acct} guest(s))"))
    print(c.dim("Recheck one with: "
                "python scripts/recheck_solutions.py check <user>"))
    return 0


# ===========================================================================
# Operation 2: recheck one user's accepted solutions
# ===========================================================================
@dataclass
class Job:
    """A single accepted solution to re-grade, detached from the DB session."""
    slug: str
    title: str
    difficulty: str
    code: str
    prob: SimpleNamespace
    tests: list[SimpleNamespace]
    submitted_at: object
    orig_passed: int
    orig_total: int


@dataclass
class Recheck:
    slug: str
    title: str
    difficulty: str
    submitted_at: object
    kind: str                    # pass | regressed | error
    now_passed: int = 0
    now_total: int = 0
    runtime_ms: float = 0.0
    error: str | None = None
    # (test SimpleNamespace, TestResult) for FAILED tests (for --verbose).
    failed_tests: list[tuple[object, object]] = field(default_factory=list)


def resolve_user(db, ident: str) -> list[User]:
    """Find users by full id, username, display name, or id prefix (in that order)."""
    u = db.get(User, ident)
    if u is not None:
        return [u]
    for column in (User.username, User.name):
        found = db.scalars(select(User).where(column == ident)).all()
        if found:
            return found
    return db.scalars(select(User).where(User.id.like(f"{ident}%"))).all()


def latest_successful_by_problem(db, user_id: str) -> dict[int, Submission]:
    """For each problem the user solved, the most recent submission that itself
    was a full pass (their accepted solution's newest revision)."""
    subs = db.scalars(
        select(Submission)
        .where(Submission.user_id == user_id, *_solved_filter())
        .order_by(Submission.created_at.desc())
    ).all()
    latest: dict[int, Submission] = {}
    for s in subs:
        latest.setdefault(s.problem_id, s)  # first seen = newest (desc order)
    return latest


def _spec_from_db(prob: Problem) -> dict:
    """Normalize a DB Problem row into the same shape content.load_problem_dir
    produces, so one builder handles both test sources."""
    return {
        "slug": prob.slug, "title": prob.title, "difficulty": prob.difficulty,
        "function_name": prob.function_name, "params": prob.params,
        "return_type": prob.return_type or "", "time_limit_ms": prob.time_limit_ms,
        "memory_limit_mb": prob.memory_limit_mb, "points": prob.points,
        "compare": prob.compare,
        "tests": [
            {"name": t.name, "input": t.input, "expected": t.expected,
             "weight": t.weight, "hidden": t.hidden}
            for t in prob.tests
        ],
    }


def _job_from_spec(spec: dict, sub: Submission) -> Job:
    """Build a session-independent Job from a spec dict (DB- or content-sourced)
    plus the user's accepted submission."""
    prob_ns = SimpleNamespace(
        function_name=spec["function_name"], params=spec.get("params", []),
        return_type=spec.get("return_type") or "", time_limit_ms=spec["time_limit_ms"],
        memory_limit_mb=spec["memory_limit_mb"], points=spec.get("points", 100),
        compare=spec.get("compare", "exact"),
    )
    tests_ns = [
        SimpleNamespace(name=t["name"], input=t["input"], expected=t["expected"],
                        weight=t.get("weight", 1), hidden=t.get("hidden", False))
        for t in spec.get("tests", [])
    ]
    return Job(
        slug=spec["slug"], title=spec["title"], difficulty=spec["difficulty"],
        code=sub.code, prob=prob_ns, tests=tests_ns, submitted_at=sub.created_at,
        orig_passed=sub.passed_count, orig_total=sub.total_count,
    )


def build_jobs(db, user_id: str,
               content_by_slug: dict[str, dict] | None = None
               ) -> tuple[list[Job], list[int], list[str]]:
    """Materialize each accepted solution into a session-independent Job so the
    actual grading can run outside the session (and in parallel).

    Tests come from the DB by default; when `content_by_slug` is given they come
    from the on-disk content instead (keyed by slug). Returns
    (jobs, orphan_problem_ids, content_miss_slugs), where orphans are submissions
    whose problem is gone from the DB, and content-misses are solved problems not
    found on disk (graded against the DB as a fallback so nothing is dropped)."""
    latest = latest_successful_by_problem(db, user_id)
    jobs: list[Job] = []
    orphans: list[int] = []
    content_misses: list[str] = []
    for pid, sub in latest.items():
        prob = db.get(Problem, pid)
        if prob is None:
            orphans.append(pid)
            continue
        spec = None
        if content_by_slug is not None:
            spec = content_by_slug.get(prob.slug)
            if spec is None:
                content_misses.append(prob.slug)  # fall through to the DB row
        if spec is None:
            spec = _spec_from_db(prob)
        jobs.append(_job_from_spec(spec, sub))
    jobs.sort(key=lambda j: j.slug)
    return jobs, orphans, content_misses


def evaluate(job: Job) -> Recheck:
    """Re-grade one accepted solution. Never raises."""
    base = dict(slug=job.slug, title=job.title, difficulty=job.difficulty,
                submitted_at=job.submitted_at)
    if not job.tests:
        # No tests today (all removed?) — nothing to fail against.
        return Recheck(**base, kind="pass", now_passed=0, now_total=0)
    try:
        graded = run_submission(job.code, job.prob, job.tests)
    except Exception as exc:  # noqa: BLE001 - surface any judge/runtime failure per-problem
        return Recheck(**base, kind="error", now_total=len(job.tests), error=str(exc))

    kind = "pass" if graded.solved else "regressed"
    failed = []
    if kind == "regressed":
        for i, r in enumerate(graded.results):
            if not r.passed:
                failed.append((job.tests[i] if i < len(job.tests) else None, r))
    return Recheck(
        **base, kind=kind,
        now_passed=graded.passed_count, now_total=graded.total_count,
        runtime_ms=graded.runtime_ms, failed_tests=failed,
    )


def print_recheck(r: Recheck, c: Palette, args) -> None:
    if r.kind == "pass":
        if args.quiet:
            return
        timing = c.dim(f"{r.runtime_ms:.0f}ms")
        print(f"{c.green('[PASS]     ')} {r.slug}: {r.now_passed}/{r.now_total} {timing}")
        return

    if r.kind == "error":
        print(f"{c.red('[ERROR]    ')} {r.slug}: could not run — {r.error}")
        return

    # regressed
    print(f"{c.red('[REGRESSED]')} {r.slug} ({r.difficulty}): "
          f"now {r.now_passed}/{r.now_total} "
          f"({_pct(r.now_passed, r.now_total)}%)  "
          + c.dim(f"accepted {_fmt_dt(r.submitted_at)}"))
    if args.verbose:
        for test, res in r.failed_tests:
            tag = c.dim("[hidden]") if res.hidden else "[visible]"
            line = f"             - {tag} {res.name} [{res.status}]"
            if res.error and res.status != "wrong":
                line += f": {res.error}"
            print(line)
            if res.status == "wrong" and test is not None:
                print(f"                 input   ={json.dumps(test.input)}")
                print(f"                 expected={json.dumps(test.expected)}")
                print(f"                 actual  ={json.dumps(res.returned)}")


def print_recheck_summary(results: list[Recheck], orphans: list[int],
                          content_misses: list[str], elapsed: float,
                          c: Palette) -> None:
    by_kind = {"pass": [], "regressed": [], "error": []}
    for r in results:
        by_kind[r.kind].append(r)

    tests_total = sum(r.now_total for r in results)
    tests_passed = sum(r.now_passed for r in results)
    n_pass, n_reg, n_err = (len(by_kind["pass"]), len(by_kind["regressed"]),
                            len(by_kind["error"]))

    print("\n" + "=" * 70)
    print(c.bold(f"Summary — {len(results)} accepted solution(s) rechecked "
                 f"in {elapsed:.1f}s"))
    print(
        f"  {c.green(f'{n_pass} still passing')}   "
        f"{c.red(f'{n_reg} regressed')}   "
        f"{c.red(f'{n_err} errored')}"
    )
    print(f"  test cases: {tests_passed}/{tests_total} passed "
          f"({_pct(tests_passed, tests_total)}%)")
    if orphans:
        print(c.yellow(f"  {len(orphans)} accepted problem(s) skipped "
                       f"(no longer in the DB)"))
    if content_misses:
        print(c.yellow(f"  {len(content_misses)} solved problem(s) not found on "
                       f"disk — graded against the DB instead: "
                       + ", ".join(sorted(content_misses))))

    if by_kind["regressed"]:
        print(c.red("\nRegressed — accepted before, fail the current suite:"))
        for r in sorted(by_kind["regressed"],
                        key=lambda r: (r.difficulty, r.slug)):
            print(f"  - {r.slug} ({r.difficulty}): "
                  f"{r.now_passed}/{r.now_total} ({_pct(r.now_passed, r.now_total)}%)")
        print(c.dim("\n  Re-solve these, or (if a test is wrong) fix the test."))
    if by_kind["error"]:
        print(c.red("\nErrored — could not run:"))
        for r in by_kind["error"]:
            print(f"  - {r.slug}: {r.error}")


def print_candidates(users: list[User], c: Palette, cap: int = 20) -> None:
    print(c.yellow(f"Ambiguous — {len(users)} users match. Pick one by id"
                   + (f" (showing first {cap})" if len(users) > cap else "") + ":"))
    # Accounts first — they're the ones you'd actually want to recheck.
    for u in sorted(users, key=lambda u: (not u.is_account, u.id))[:cap]:
        kind = "account" if u.is_account else "guest"
        print(f"  {u.id[:12]}  {_user_label(u):<20} ({kind})")


def run_check(db, c: Palette, args) -> int:
    matches = resolve_user(db, args.user)
    if not matches:
        print(c.red(f"No user matches {args.user!r}. "
                    f"List users with: python scripts/recheck_solutions.py users"))
        return 2
    if len(matches) > 1:
        print_candidates(matches, c)
        return 2
    user = matches[0]

    content_by_slug = None
    if args.from_content:
        content_by_slug = {p["slug"]: p for p in content.load_all_roots()}

    jobs, orphans, content_misses = build_jobs(db, user.id, content_by_slug)
    # Everything the grader needs is now detached from the session.
    if not jobs:
        print(f"{_user_label(user)} has no solved problems to recheck.")
        return 0

    source = ("on-disk content/ (freshest)" if args.from_content
              else "the DB test suite")
    print(c.bold(f"Rechecking {len(jobs)} accepted solution(s) for "
                 f"{c.cyan(_user_label(user))} "
                 + c.dim(f"({user.id[:12]})")
                 + (f" with {args.jobs} workers" if args.jobs > 1 else ""))
          + c.dim(f"\nGrading against {source}.\n"))

    results: list[Recheck] = []
    start = time.perf_counter()
    if args.jobs <= 1:
        for job in jobs:
            r = evaluate(job)
            results.append(r)
            print_recheck(r, c, args)
    else:
        # Threads are safe: each Job is self-contained and run_submission spawns
        # its own subprocess/temp dir. Lines print in completion order.
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            futures = {pool.submit(evaluate, j): j for j in jobs}
            for fut in as_completed(futures):
                r = fut.result()
                results.append(r)
                print_recheck(r, c, args)

    elapsed = time.perf_counter() - start
    print_recheck_summary(results, orphans, content_misses, elapsed, c)

    bad = sum(1 for r in results if r.kind in ("regressed", "error"))
    return 1 if bad else 0


# ===========================================================================
# CLI
# ===========================================================================
from datetime import datetime, timezone  # noqa: E402

_EPOCH = datetime(1970, 1, 1, tzinfo=timezone.utc)


def main(argv: list[str] | None = None) -> int:
    # --no-color is shared, so it's accepted before OR after the subcommand.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--no-color", action="store_true",
                        help="disable colored output")

    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[common],
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_users = sub.add_parser("users", parents=[common],
                             help="list all users with activity stats")
    p_users.add_argument("--all", action="store_true",
                         help="include users with zero submissions (guests)")

    p_check = sub.add_parser(
        "check", parents=[common],
        help="re-grade one user's accepted solutions vs current tests")
    p_check.add_argument("user",
                         help="username, display name, full id, or id prefix")
    p_check.add_argument("-v", "--verbose", action="store_true",
                         help="for regressions, show each failing test "
                              "(input/expected/actual)")
    p_check.add_argument("-q", "--quiet", action="store_true",
                         help="suppress per-problem PASS lines; show only "
                              "regressions + summary")
    p_check.add_argument("-j", "--jobs", type=int, default=1, metavar="N",
                         help="recheck N problems in parallel (default: 1)")
    p_check.add_argument("--from-content", action="store_true",
                         help="grade against the freshest tests on disk "
                              "(content/problems/<slug>/) instead of the DB — "
                              "no re-seed needed")

    args = ap.parse_args(argv)
    c = Palette(enabled=not args.no_color and sys.stdout.isatty())

    init_db()  # ensure tables/migrations exist; harmless if already seeded
    db = SessionLocal()
    try:
        if args.cmd == "users":
            return print_users(db, c, args)
        if args.cmd == "check":
            return run_check(db, c, args)
    finally:
        db.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
