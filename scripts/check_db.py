#!/usr/bin/env python3
"""Check that the local database is physically intact.

Runs `PRAGMA quick_check` (a page/index consistency pass, without the slower
full cross-reference of `integrity_check`) and reports what to do about it.

This exists because of a real incident: `.gitignore` covered `*.db` but not
`*.db-wal`, so the SQLite write-ahead log was tracked while the database it
belongs to was ignored, and a `git stash` swapped the log out from under the
data file. The result was cross-table page sharing — `collection_problems` rows
surfacing inside `test_cases` — and the symptom was a 500 on `/admin` with
`json.loads(<int>)`, half an hour away from its cause. See
`docs/database.md` and `docs/retrospectives/2026-07-28-database-corruption.md`.

It runs FIRST in `make check-bank`, before `seed.py`, for two reasons: seeding a
damaged database writes into it and can spread the damage, and a clear
"the database is corrupt" beats a `TypeError` from inside a JSON column decoder.

Exit codes: 0 intact (or absent — a fresh checkout has no database yet),
1 damaged.
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings  # noqa: E402

ADVICE = """
The database is damaged. It was almost certainly not the application that did
this — corruption at this level is below the SQL layer.

  1. Stop anything using it (the dev server, a `make` run).
  2. Back up ALL THREE files together — a .db without its -wal is missing the
     most recent transactions:
       cp lootcode.db lootcode.db-wal lootcode.db-shm /tmp/dbbackup/
  3. Salvage it. `.recover` reads what is readable and rebuilds a clean file:
       sqlite3 lootcode.db ".recover" > /tmp/recovered.sql
       rm lootcode.db lootcode.db-wal lootcode.db-shm
       sqlite3 lootcode.db < /tmp/recovered.sql
  4. Restore anything it had to drop. Problems, tests and collections are
     derived from content/, so re-seeding replaces them:
       python scripts/seed.py --no-verify
     Accounts, submissions and solved history are NOT derived and exist only
     here — check the counts before and after.
  5. Confirm: python scripts/check_db.py

If you were switching branches or stashing when this appeared, see
docs/database.md — git must never track a database file or its -wal/-shm.
"""


def check(path: Path, *, full: bool = False) -> int:
    if not path.exists():
        print(f"No database at {path} — nothing to check (it is created on first run).")
        return 0

    pragma = "integrity_check" if full else "quick_check"
    try:
        # Read-only, and immutable so a damaged file cannot be written to or
        # have a stale WAL replayed into it just by looking at it.
        con = sqlite3.connect(f"file:{path}?immutable=1", uri=True)
        rows = [r[0] for r in con.execute(f"PRAGMA {pragma}").fetchall()]
        con.close()
    except sqlite3.DatabaseError as exc:
        print(f"FAIL: {path} could not be opened as a SQLite database: {exc}")
        print(ADVICE)
        return 1

    if rows == ["ok"]:
        size_mb = path.stat().st_size / 1e6
        print(f"OK: {path} is intact ({pragma}, {size_mb:.1f} MB).")
        return 0

    print(f"FAIL: {path} failed PRAGMA {pragma}:")
    for line in rows[:20]:
        print(f"  {line}")
    if len(rows) > 20:
        print(f"  ... and {len(rows) - 20} more")
    print(ADVICE)
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--db", type=Path, default=None,
                        help="database to check (default: settings.DB_PATH)")
    parser.add_argument("--full", action="store_true",
                        help="PRAGMA integrity_check — slower, also cross-checks indexes")
    args = parser.parse_args(argv)
    return check(args.db or Path(settings.DB_PATH), full=args.full)


if __name__ == "__main__":
    raise SystemExit(main())
