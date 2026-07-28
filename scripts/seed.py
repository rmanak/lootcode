"""Seed the database from content/problems/ and verify canonical solutions.

Usage:  python scripts/seed.py               (from the project root)
        python scripts/seed.py -j 8          verify in parallel
        python scripts/seed.py --no-verify   seed only, skip verification

Seeding itself takes a couple of seconds; the rest of the time is running every
canonical solution through the sandbox, one at a time. That is the *same work*
``scripts/verify_bank.py -j`` does in a fraction of the time, so if you are about
to run that anyway (as ``make check`` does), seed with ``--no-verify``.
"""
from __future__ import annotations

import argparse
import pathlib
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from types import SimpleNamespace

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from sqlalchemy.orm import selectinload  # noqa: E402

from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import problem_view, run_submission  # noqa: E402
from app.models import Problem  # noqa: E402
from app.store import seed_collections, seed_from_content  # noqa: E402


def _snapshot(problems) -> list[tuple]:
    """Detach what verification needs from the ORM.

    Worker threads must never touch the Session — a lazy load from several
    threads at once is not safe — so each item is a plain, already-materialized
    ``(slug, canonical, ProblemView, tests)``. ``ProblemView`` is frozen for
    exactly this purpose.
    """
    return [
        (p.slug, p.canonical_solution, problem_view(p),
         [SimpleNamespace(name=t.name, input=t.input, expected=t.expected,
                          weight=t.weight, hidden=t.hidden) for t in p.tests])
        for p in problems if p.canonical_solution
    ]


def _verify(item: tuple) -> tuple[str, bool, int, int]:
    """Grade one problem's canonical against its own tests."""
    slug, canonical, view, tests = item
    graded = run_submission(canonical, view, tests)
    return slug, graded.solved, graded.passed_count, graded.total_count


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-j", "--jobs", type=int, default=1, metavar="N",
                    help="verify with N worker threads (default 1). Each run gets "
                         "its own subprocess and temp dir, so threads are safe.")
    ap.add_argument("--no-verify", action="store_true",
                    help="seed only. Use when verify_bank.py runs next — it does "
                         "the same work, in parallel.")
    ap.add_argument("-q", "--quiet", action="store_true",
                    help="report only failures, not every passing problem")
    args = ap.parse_args(argv)

    init_db()
    with SessionLocal() as db:
        n = seed_from_content(db)
        print(f"Seeded/updated {n} problem(s).")

        failures = 0
        if args.no_verify:
            print("Skipped canonical verification (--no-verify).")
        else:
            # Eager-load `tests`: the snapshot below would otherwise lazy-load,
            # and with -j that happens from several threads against one Session.
            problems = list(
                db.query(Problem).options(selectinload(Problem.tests)).all())
            for slug in sorted(p.slug for p in problems if not p.canonical_solution):
                print(f"  - {slug}: no canonical solution (skipped verification)")

            work = _snapshot(problems)
            start = time.perf_counter()
            if args.jobs > 1:
                with ThreadPoolExecutor(max_workers=args.jobs) as pool:
                    futures = [pool.submit(_verify, item) for item in work]
                    results = [f.result() for f in as_completed(futures)]
            else:
                results = [_verify(item) for item in work]
            elapsed = time.perf_counter() - start

            for slug, solved, passed, total in sorted(results):
                if not solved:
                    failures += 1
                elif args.quiet:
                    continue
                print(f"  [{'OK ' if solved else 'FAIL'}] {slug}: canonical passed "
                      f"{passed}/{total} tests")
            print(f"\nVerified {len(results)} canonical(s) in {elapsed:.1f}s"
                  f"{f' across {args.jobs} workers' if args.jobs > 1 else ''}.")

        if failures:
            print(f"\n{failures} problem(s) have a canonical solution that does NOT "
                  "pass all tests — fix the content.")

        # Curated lists (content/collections/*.json). A collection may reference a
        # slug that isn't present — an extended/gitignored problem on a default-only
        # checkout, or a stale/typo'd slug. Either way the reference is skipped, not
        # fatal: it's reported for a maintainer's eye but never fails seeding.
        n_coll, unresolved = seed_collections(db)
        print(f"\nSeeded/updated {n_coll} collection(s).")
        if unresolved:
            print(f"  {len(unresolved)} collection reference(s) skipped (problem not "
                  "present — e.g. an extended/gitignored problem, or a stale slug):")
            for ref in unresolved:
                print(f"    - {ref}")
        return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
