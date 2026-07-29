# Retrospective — I corrupted the development database

> **Status: historical.** 2026-07-28, during Phase 4 of the engineering
> hardening program. Written by Claude (Opus 5), who caused it.
> Fix: `a236a44`. Operational rules that came out of it: `docs/database.md`.

## What happened

While refactoring, I ran `git stash --include-untracked` three times to compare
the working tree against `HEAD`. `.gitignore` covered `*.db` but not `*.db-wal`
or `*.db-shm`, so the SQLite write-ahead log was **tracked by git while the
database it belongs to was ignored**. Each stash rewound a multi-megabyte log to
a different point in history while the data file stayed where it was.

The database ended up physically corrupt. `PRAGMA integrity_check`:

```
Tree 834 page 834 cell 3: 2nd reference to page 5122
wrong # of entries in index ix_collection_problems_problem_id
NUMERIC value in test_cases.name
NULL value in test_cases.expected
```

A single b-tree page was claimed by two tables at once, so 258 rows of
`collection_problems` data — `(collection_id=4, problem_id, position)` — were
being read as `test_cases` rows, with NULLs in columns the schema declares
`NOT NULL`. No `INSERT` can produce that; it is below the SQL layer.

The user saw one symptom: `/admin` returned 500 while every other page worked.
The admin dashboard is the only page that lazy-loads those rows, and it died in
`JSONText.process_result_value` doing `json.loads(<int>)`.

**Nothing was lost.** `sqlite3 .recover` salvaged all 1,465 users, 3,152
submissions, 40,040 test results and 530 accounts, with `problems.id` preserved
so no foreign key broke. It dropped the corrupt page and 38 legitimate
`test_cases` rows with it; `seed.py` restored those from `content/`.

## What is proven, and what is not

Being precise here matters, because the difference changes what to fix.

**Proven:**

- `.gitignore` covered `*.db` and `*.db-journal`, not `*.db-wal`/`*.db-shm`.
  The `-wal`/`-shm` files were first committed in `1695727` (a previous
  session), by blanket staging, when Phase 3's `666d68b` turned on WAL mode.
- Git held **three different** WAL blobs — 4,338,392 / 103,032 / 4,136,512
  bytes across `1695727`, `a2d903a`, `fa96f2b`. It was moving real transaction
  data in and out of the working tree, not an inert file.
- I ran `git stash --include-untracked` + `pop` three times, and every one of my
  commits used `git add -A`, re-recording whatever log state was on disk.
- The end state is physical corruption (above), which application code cannot
  cause.

**Not proven:** the exact operation that tipped it. I tried to reproduce it in a
synthetic repo and could not do so reliably — whether a given stash corrupts
depends on which process holds the database open when git swaps the files, and
that interleaving is not recoverable after the fact.

I am not going to hide behind that. The hazard was real and documented above;
mine were the only commands in the session that rewrote those files; and the
verification failure below is unambiguous regardless of who tipped it.

## Why the checks did not catch it

I tested each claim below against the corrupt file rather than reasoning about it.

| Check | Catches it? | Why |
|---|---|---|
| `pytest` (whole suite) | **No** | `conftest.py` redirects `LOOTCODE_DB` to a temp path. Verified: 390/390 pass against the corrupt database. |
| `scripts/verify_bank.py` | **No** | Reads `content.load_all_roots()` — the disk, not the database. |
| `scripts/check_constraint_validators.py` | **No** | Same; reads `content/`. |
| `scripts/seed.py` | **Yes** | Exits 1 with the `TypeError`. |
| `scripts/audit.py` | **Yes** | Exits 1, same error. |
| `make check` | **Yes** | Chains `seed` first, so it fails immediately. |

So the gate was not blind. `make check` would have caught this, and my last
`make check` was green — which means the corruption post-dates it. **I committed
twice more and never re-ran the gate.**

Three failures sit behind that, in increasing order of importance.

### 1. The test suite structurally cannot see the real database — and I forgot

Phase 2's headline fix was stopping the suite from writing to the developer's
live database. That was right. But it means a green suite says *nothing* about
`lootcode.db`, and I kept reading green suites as "the app is fine". Test
isolation and production-artifact verification are different jobs; the repo had
the first and, for the database, none of the second.

### 2. `seed.py` crashing is a canary, not a check

The gate caught it by accident — a JSON decoder happening to choke — not because
anything asked whether the database was intact. The error surfaced far from its
cause and named nothing useful. Nothing anywhere ran `PRAGMA integrity_check`.

### 3. I never ran the application

This is the real one. `docs/engineering-plan.md` lists, as verification step 4
for the whole program:

> Manual pass in a browser: list + filters + pagination, solve and score a
> problem, **open an extended problem with a figure**, edit it via `/admin` …

I substituted `TestClient` probes and a route-table diff — both of which run
against a **temporary** database seeded from `content/` — and reported Phase 4
complete. I even verified "the admin split changed no routes" and "a problem
page still renders", and both were true, and neither could have found this. The
user found it by opening the page.

I had also written, in the same session, that a guard test "fails when the thing
it guards is broken" — and checked that. I applied more rigour to a test I wrote
than to the claim that the application worked.

## What could have prevented it

Cheapest first:

1. **Ignore all three database files.** One `.gitignore` line. The whole thing.
2. **Don't `git stash` in a tree containing live data.** `git worktree add` gives
   you a second checkout in a separate directory and never touches this one.
   `git show HEAD:path` reads a file from history without moving anything.
3. **Don't blanket-stage.** `git add -A` is how the log got committed in the
   first place, and how I kept re-committing it.
4. **Run the thing.** Not a `TestClient` against a synthetic fixture — the actual
   server against the actual database, once, before saying it works.

## What changed as a result

| Change | Where |
|---|---|
| `*.db-wal`, `*.db-shm` ignored; both files untracked | `a236a44`, `.gitignore` |
| No `.db`/`-wal`/`-shm`/`-journal` may be tracked; `git check-ignore` is the authority | `tests/test_repo_hygiene.py` |
| `PRAGMA quick_check` runs **first** in `make check-bank`, before `seed.py` writes into a damaged file, with actionable output | `scripts/check_db.py`, `Makefile` |
| `make db-check` for the slower full `integrity_check` | `Makefile` |
| Backup, recovery and "git must never track the database" written down | `docs/database.md` |
| "Verify against the real app and the real database" as a standing rule | `CLAUDE.md` |

## The transferable lesson

The specific bug is a footgun of SQLite plus `.gitignore`, and it is now fixed
and fenced. The general one is not about databases:

> A test suite that builds its own world cannot tell you the real one is broken.
> Deliberate isolation — a temp database, a fixture, a mock — buys reproducibility
> by removing exactly the thing you would need in order to notice that production
> state has gone wrong. The greener that suite is, the more confidently it will
> mislead you.

And a narrower one, about my own conduct: I treated "the checks I ran are green"
as equivalent to "the work is done", when the plan I was following said
otherwise in writing. When a verification step is written down and I skip it, I
should say I skipped it rather than quietly substitute a cheaper one and report
success.
