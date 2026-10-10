# ICF — the Industry Coding Framework

Timed, four-level assessments in the CodeSignal "industry coding" shape: you
implement **one class** from a template, each level adds requirements while
everything below it must keep passing, and a level unlocks only when every one
of its tests — visible *and* hidden — goes green. 90 minutes by default.

It is an **optional extension** (see `docs/extensions.md`): delete this folder
and lootcode is exactly what it was. Nothing under `app/` imports anything
from here.

```
/icf                     the problem list
/icf/<slug>              the workspace: statement, editor, run/submit, clock
/icf/attempts/<id>       what happened in one sitting
/api/icf/...             start, run, submit, autosave, finish
```

## Layout

| Path | What it is |
|---|---|
| `__init__.py` | `register(app)` — the one entry point core calls |
| `config.py` | settings, all from `ICF_*` env vars with working defaults |
| `content.py` | load + validate problems from `problems/`; nothing is executed |
| `db.py`, `models.py` | its **own** SQLite file (`icf/data/icf.db`), never `lootcode.db` |
| `store.py` | attempt lifecycle: the clock, unlocking, runs, drafts |
| `runner.py` | grade a submission through core's sandbox |
| `sandbox/harness.py` | runs **inside** the sandbox (stdlib only, no app imports): a supervisor that writes the results and a forked worker that runs the solution |
| `sandbox/testkit.py` | `@case` / `expect` — copied into the run directory |
| `views.py` | JSON shaping, and the hidden-test redaction rule |
| `routers/` | `pages.py` (HTML) and `api.py` (JSON) |
| `problems/<slug>/` | the problems — see `docs/problem-format.md` |
| `scripts/verify_icf.py` | the gate: every canonical passes, every level earns its place |
| `tests/` | collected automatically by the root `conftest.py` |

## Commands

```bash
python icf/scripts/verify_icf.py            # verify every problem
python icf/scripts/verify_icf.py --slug in-memory-database -v
make icf-verify                             # the same, and part of `make check`
python -m pytest icf/tests -q               # the extension's own suite
```

## Data

`icf/data/icf.db` holds attempts, runs and submitted code — **user data**, and
the only copy of it. Back it up with its `-wal`/`-shm` siblings, the same rule
`docs/database.md` sets for `lootcode.db`. Deleting it loses attempt history
and nothing else: problems live on disk.

Settings: `ICF_DB`, `ICF_PROBLEMS_DIR`, `ICF_TIME_CAP_MINUTES`,
`ICF_CASE_TIME_LIMIT_MS`, `ICF_MEMORY_LIMIT_MB`, `ICF_MAX_OUTPUT_KB`.

## Docs

* `docs/problem-format.md` — how to author a problem
* `docs/design.md` — why the pieces are shaped the way they are
* `docs/security.md` — what is trusted, what is not
