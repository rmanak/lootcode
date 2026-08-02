# Removing a problem from the bank

`scripts/remove_problem.py` retires a problem: its content directory, every
collection manifest that names it, and every database row keyed to it.

```bash
python scripts/remove_problem.py <slug>                  # retire outright
python scripts/remove_problem.py <old-slug>=<new-slug>   # dedupe: point refs at the twin
python scripts/remove_problem.py --from-file dupes.txt   # a batch of either
```

## Why a script

A slug lives in more places than its directory:

| Where | What holds it |
|---|---|
| `content/problems[-extended]/<slug>/` | statement, meta, tests, canonical, starter, input validator, assets |
| `content/collections/*.json` | the slug, **by name**, in a curated study order |
| `problems` | the row every other table's `problem_id` points at |
| `test_cases`, `collection_problems` | derived rows, rebuilt by seeding |
| `submissions` → `test_results` | **user data** — graded attempts and their per-test detail |
| `known_problems`, `visit_later_problems` | **user data** — personal marks |

Delete only the directory and the problem stays live in the app, served from the
DB. Delete only the row and the manifests keep naming a slug that resolves to
nothing. The script does both, in an order that never leaves a dangling
reference, then re-seeds collections so the `position` sequence closes the hole
the removed member left.

## Deduplicating

When the problem is a twin of one already in the bank, give the survivor:

```bash
python scripts/remove_problem.py two-sum-ii=two-sum
```

Every collection that referenced the loser then references the winner **in the
loser's position** — a curated list keeps both its order and its length, instead
of quietly getting shorter. If a list already contains the survivor, the
reference is dropped rather than duplicated; a curated list must never name the
same problem twice. A subtitle that states the list's size ("A curated set of 196
problems") is restated when the size actually changes.

`old=new` and `old->new` are equivalent, on the command line or one per line in a
`--from-file` list (`#` comments allowed).

## User data

**Submissions against a removed problem are deleted by default**, along with
their test results. The report says how many and whose before anything is
written, and the confirmation prompt calls the number out again.

`--migrate-submissions` repoints them at the replacement instead. Reasonable for
a true duplicate — but the scores were computed against the *removed* problem's
tests, so a migrated submission's pass count may not correspond to the
survivor's suite. `known`/`visit later` marks migrate too, except where the user
already marked the survivor (those rows are `UNIQUE(user_id, problem_id)`, so
the redundant one is dropped rather than collided).

The database is snapshotted first either way, into `scratchpad/db-backups/`
(gitignored) via SQLite's backup API — not `cp`, which can catch a live WAL
database mid-transaction, and the dev server is usually running. `--backup-dir`
moves it, `--no-backup` skips it.

> Keep backups out of the repo root. `.gitignore` covers `*.db` but **not**
> `*.db.bak-*`, so a backup left at the root is stageable — the exact shape of
> the accident in `docs/retrospectives/2026-07-28-database-corruption.md`.

## Safety

Nothing is written until every slug resolves *and* you confirm. The script
aborts, having written nothing, if any slug is unknown, if a replacement is not
in the bank, if a replacement is itself being removed, or if a slug is listed
twice. `--dry-run` reports and stops; `-y/--yes` skips the prompt for scripted
runs.

Afterwards it runs `PRAGMA quick_check`, verifies no submission was orphaned, and
exits non-zero if either fails.

## After

```bash
make check     # lint + types + tests + the whole bank
```

The removal itself re-seeds collections, so the app picks the change up without a
restart. Confirm on the running server that `/problems/<slug>` is a 404 and the
affected collection pages still render — see the "done means the real thing ran"
rule in `CLAUDE.md`.
