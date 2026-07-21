"""Seed (upsert) a single problem by slug from content/ into the DB, and verify
its canonical solution. A fast one-slug alternative to scripts/seed.py when you
only changed one problem (e.g. edited hints/tests) and don't want a full-bank
re-seed + verify.

Usage:  python scripts/seed_one.py <slug>
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app import content  # noqa: E402
from app.config import settings  # noqa: E402
from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.store import upsert_problem  # noqa: E402


def main(slug: str) -> int:
    for base in settings.content_dirs:
        d = base / slug
        if d.is_dir():
            data = content.load_problem_dir(d)
            break
    else:
        print(f"slug not found in any content root: {slug}")
        return 2

    init_db()
    with SessionLocal() as db:
        prob = upsert_problem(db, data)
        print(f"Upserted {prob.slug}.")
        if not prob.canonical_solution:
            print("  - no canonical solution (skipped verification)")
            return 0
        graded = run_submission(prob.canonical_solution, prob, prob.tests)
        ok = "OK " if graded.solved else "FAIL"
        print(f"  [{ok}] {prob.slug}: canonical passed "
              f"{graded.passed_count}/{graded.total_count} tests")
        return 0 if graded.solved else 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python scripts/seed_one.py <slug>")
        raise SystemExit(2)
    raise SystemExit(main(sys.argv[1]))
