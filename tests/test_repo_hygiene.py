"""Things that must not be committed.

The database is a *derived* artifact — `content/` is the durable source of truth
for problems — but it is also the only home for user data: accounts, submissions,
solved history, known/visit-later flags. None of that is regenerable, so the
rules about which database files git may touch are worth enforcing by machine.

## The incident this exists to prevent

`.gitignore` listed `*.db` and `*.db-journal` but not `*.db-wal` / `*.db-shm`.
When Phase 3 turned on `journal_mode=WAL` (`app/db.py`), those two siblings
started existing and were committed — so the write-ahead log was tracked while
the data file it belongs to was ignored.

They are not separate files in any meaningful sense: the WAL holds committed
transactions that have not yet been folded back into the main database. Checking
out, stashing, or switching branches rewrites the log to a different point in
history while the ignored `.db` stays where it is. SQLite then replays a WAL that
does not match the data file. The result is not a clean rollback, it is physical
corruption: `PRAGMA integrity_check` reported `2nd reference to page 5122` — a
b-tree page belonging to `collection_problems` also being read as part of
`test_cases`, which surfaced as 258 rows in `test_cases` holding collection data
and violating that table's own NOT NULL constraints. `/admin` 500'd on
`json.loads(<int>)` while every other page rendered fine.

## How it was recovered, if it ever happens again

`sqlite3 lootcode.db ".recover" > out.sql` then replaying that into a fresh file
salvaged everything — all 1,465 users, 3,152 submissions and 40,040 test results,
with problem ids preserved so no foreign key broke. It dropped the corrupt rows
and 38 legitimate `test_cases` rows along with them, which `scripts/seed.py`
restored from `content/`. Back up all three files first: a copy of `.db` without
its `-wal` is missing the most recent transactions.
"""
from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parent.parent


def _tracked_files() -> list[str]:
    out = subprocess.run(
        ["git", "ls-files"], cwd=_ROOT, capture_output=True, text=True, check=True)
    return out.stdout.splitlines()


def test_git_is_available_here():
    """Guard the guard: without this, a failure to shell out reads as a pass."""
    assert _tracked_files(), "git ls-files returned nothing — is this a checkout?"


@pytest.mark.parametrize("suffix", [".db", ".db-wal", ".db-shm", ".db-journal"])
def test_no_sqlite_file_is_tracked(suffix):
    """Every piece of a SQLite database is ignored, or none of it should be.

    Tracking one part while ignoring another is the specific configuration that
    corrupts the database on any checkout — see this module's docstring.
    """
    tracked = [f for f in _tracked_files() if f.endswith(suffix)]
    assert not tracked, (
        f"{tracked} is tracked by git. A SQLite database and its -wal/-shm "
        "siblings are one artifact: tracking part of it means a checkout can "
        "replay a mismatched write-ahead log over the data file and corrupt it.")


def test_the_database_is_ignored_in_practice_not_just_by_pattern():
    """`git check-ignore` is the authority, not our reading of .gitignore."""
    names = ["lootcode.db", "lootcode.db-wal", "lootcode.db-shm"]
    out = subprocess.run(["git", "check-ignore", "-v", *names],
                         cwd=_ROOT, capture_output=True, text=True)
    ignored = {line.rsplit("\t", 1)[-1] for line in out.stdout.splitlines()}
    missing = [n for n in names if n not in ignored]
    assert not missing, f"{missing} would be committable"
