"""Seed the database from content/problems/ and verify canonical solutions.

Usage:  python scripts/seed.py        (from the project root)
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

from app.db import SessionLocal, init_db  # noqa: E402
from app.executor import run_submission  # noqa: E402
from app.models import Problem  # noqa: E402
from app.store import seed_collections, seed_from_content  # noqa: E402


def main() -> int:
    init_db()
    with SessionLocal() as db:
        n = seed_from_content(db)
        print(f"Seeded/updated {n} problem(s).")

        problems = list(db.query(Problem).all())
        failures = 0
        for p in problems:
            if not p.canonical_solution:
                print(f"  - {p.slug}: no canonical solution (skipped verification)")
                continue
            graded = run_submission(p.canonical_solution, p, p.tests)
            ok = "OK " if graded.solved else "FAIL"
            print(f"  [{ok}] {p.slug}: canonical passed "
                  f"{graded.passed_count}/{graded.total_count} tests")
            if not graded.solved:
                failures += 1
        if failures:
            print(f"\n{failures} problem(s) have a canonical solution that does NOT "
                  "pass all tests — fix the content.")

        # Curated lists (content/collections/*.json).
        n_coll, unresolved = seed_collections(db)
        print(f"\nSeeded/updated {n_coll} collection(s).")
        if unresolved:
            print(f"  {len(unresolved)} unknown problem slug(s) referenced (skipped):")
            for ref in unresolved:
                print(f"    - {ref}")
            print("  Fix the manifest slug or add the missing problem.")
        return 1 if (failures or unresolved) else 0


if __name__ == "__main__":
    raise SystemExit(main())
