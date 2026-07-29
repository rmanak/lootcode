# The database

> **Status: normative.** Rules and procedures for `lootcode.db`. If you are here
> because something is broken, jump to [Recovery](#recovery).

SQLite, one file, at `settings.DB_PATH` (`LOOTCODE_DB`, default `./lootcode.db`).
Schema in `app/models.py`, engine and pragmas in `app/db.py`.

## What is derived and what is not

This distinction decides everything else on this page.

| Table | Source of truth | If lost |
|---|---|---|
| `problems`, `test_cases` | `content/problems/`, `content/problems-extended/` | `python scripts/seed.py` restores it |
| `collections`, `collection_problems` | `content/collections/*.json` | ditto |
| `users` | **the database** | **gone** |
| `submissions`, `test_results` | **the database** | **gone** |
| `known_problems`, `visit_later_problems` | **the database** | **gone** |

The bank is a cache of `content/`. Everything a *person* did — their account,
their submissions, what they have solved, what they marked known or flagged for
later — exists only here and is not in git. Treat the file accordingly.

There are no migrations: `init_db` runs `create_all`, so adding a column means
either recreating the database or issuing the `ALTER` yourself.

## git must never track any part of the database

`.gitignore` covers `*.db`, `*.db-wal`, `*.db-shm` and `*.db-journal`, and
`tests/test_repo_hygiene.py` fails the build if any of them is tracked. That test
is not bureaucracy — it exists because the opposite configuration corrupted this
database once already.

A SQLite database in WAL mode (which this is, see `app/db.py`) is **three files
that are one artifact**:

- `lootcode.db` — the data
- `lootcode.db-wal` — the write-ahead log: committed transactions not yet folded
  back into the data file, routinely several megabytes
- `lootcode.db-shm` — the shared-memory index into that log

Tracking one while ignoring another means git rewrites part of a live database
whenever you check out, stash, rebase, or switch branches, and SQLite then reads
a log that does not describe the data file next to it. That is not a stale read
you can refresh away; it is physical corruption — b-tree pages claimed by two
tables at once. The symptom is arbitrary and far from the cause. Ours was a 500
on `/admin` from `json.loads(<int>)`.

The same applies to any tool that "helpfully" snapshots a working tree.

### Before any git operation that rewrites the working tree

**Stop the dev server first.** A running `uvicorn` holds all three files open at
once (`/proc/<pid>/fd` shows `.db`, `.db-wal` and `.db-shm`), and the
shared-memory index describes the log that was there when it opened. Rewriting
those files underneath it is the dangerous case — and since the server is
normally up while you work, it is the default case rather than an unlucky one.

Nothing else needs doing *now* that the ignore rules are right. But if you are on an
older checkout — anything before `a236a44`, where `lootcode.db-wal` is still in
the tree — delete `lootcode.db-wal` and `lootcode.db-shm` **before** starting the
app, so a log from that commit is never replayed over your current data.

Prefer `git worktree add` over `git stash` when you need a second version of the
tree to compare against. A worktree is a separate directory; a stash mutates the
one your database is sitting in.

## Backups

There is no backup automation. To take one, stop the app and copy **all three
files together** — a `.db` copied without its `-wal` is missing the most recent
transactions:

```bash
cp lootcode.db lootcode.db-wal lootcode.db-shm /somewhere/safe/
```

Or, without stopping anything, let SQLite make a consistent copy:

```bash
sqlite3 lootcode.db ".backup /somewhere/safe/lootcode.db"
```

## Checking it

```bash
python scripts/check_db.py          # PRAGMA quick_check — fast
make db-check                       # PRAGMA integrity_check — slower, checks indexes too
```

`make check` runs the fast one **first**, before `seed.py`, so a damaged database
is reported as damaged instead of surfacing as a `TypeError` from inside a JSON
column decoder several steps later — and so seeding does not write into a file
that is already broken.

## Recovery

If `check_db.py` fails:

1. **Stop everything** touching the file — the dev server, any `make` run.
2. **Back up all three files** (above). Do this before anything else; recovery
   steps are destructive and you may want a second attempt.
3. **Salvage.** `.recover` reads what is readable and rebuilds a clean file. It
   recovers far more than you would expect — in the 2026-07-28 incident it kept
   every one of 1,465 users, 3,152 submissions and 40,040 test results, with
   `problems.id` values preserved so no foreign key broke.
   ```bash
   sqlite3 lootcode.db ".recover" > /tmp/recovered.sql
   rm lootcode.db lootcode.db-wal lootcode.db-shm
   sqlite3 lootcode.db < /tmp/recovered.sql
   ```
4. **Check what it dropped.** Compare row counts against the backup. Anything
   missing from `problems`/`test_cases`/`collections` is derived — re-seed:
   ```bash
   python scripts/seed.py --no-verify
   ```
   Anything missing from `users`/`submissions`/`test_results` is *not* derived.
   If those counts dropped, say so rather than quietly moving on.
5. **Verify.**
   ```bash
   python scripts/check_db.py --full
   make check
   ```

Rebuilding from scratch (`rm lootcode.db && python scripts/seed.py`) restores the
bank and destroys every account and submission. It is the right move only on a
machine whose database holds nothing but seeded content.

## Configuration

`app/db.py` sets, on every connection:

| Pragma | Value | Why |
|---|---|---|
| `journal_mode` | `WAL` | readers do not block the writer; the default rollback journal serialized every request behind any write |
| `busy_timeout` | 5000 ms | the default is 0 — a concurrent write failed instantly rather than waiting |
| `foreign_keys` | `ON` | SQLite does not enforce them otherwise |

WAL is what creates the `-wal`/`-shm` siblings, and therefore what made the
git-tracking hazard possible. It is still the right setting; the fix is to ignore
the files, not to give up concurrency.

## Tests never touch it

`tests/conftest.py` points `LOOTCODE_DB` at a temporary file *before* anything
imports `app.config`, and `pytest_configure` fails the run outright if that did
not take. The suite used to run against the live database, inserting real users
and mutating collections.

The consequence is worth stating plainly, because it bit us: **the test suite
cannot observe the real database, so a green suite says nothing about the health
of `lootcode.db`.** That is the job of `check_db.py` and of actually opening the
app. See `docs/retrospectives/2026-07-28-database-corruption.md`.
