# Industry Coding Framework (ICF) — implementation plan

**Status: a plan, not a description.** Nothing in `icf/` exists yet; the paths
below are the design, and `docs/icf-plan.md` is listed in
`tests/test_docs_consistency.py::FORWARD_LOOKING` for that reason. Source
brief: `icf.txt` (kept out of git).

---

## 1. What we are building

A second problem *format* alongside the existing LeetCode-style bank: the
CodeSignal "Industry Coding Framework" assessment used by Anthropic and others.

One ICF problem is a small realistic system (an in-memory database, a banking
ledger, a recipe service) delivered as **four levels that stack**:

| Property | Rule |
|---|---|
| Levels | Exactly 4. Level *N* adds requirements; levels 1…*N−1* must still pass. |
| Solution shape | **One class**. The starter is a template with every method declared and empty bodies. Code carries forward between levels — the solver refactors, never restarts. |
| Grading | Per-level unit tests, **visible** (name, failure message, STDOUT) and **hidden** (pass/fail only). Exhaustive on edge cases, light on algorithms. |
| Gating | Level *N+1* unlocks only when every level-*N* test passes. |
| Clock | 90-minute hard cap per attempt, server-authoritative. A practice mode runs untimed. |

This is a different beast from `content/problems/`: no single `function_name`,
no `(input, expected)` JSON pairs, no `compare` mode — assertions live in
authored Python test modules, and an attempt is a stateful 90-minute session,
not a submission.

## 2. The hard constraint: a removable feature

> All ICF code lives in one sub-folder, and the app works identically with or
> without it — present ⇒ the feature exists and is visible; absent ⇒ as if it
> never existed.

So `icf/` is an **optional extension package** at the repo root, and core gains
exactly three *generic* seams — none of which names ICF, all of which are
no-ops when no extension is installed.

### Seam 1 — `app/extensions.py` (new, ~50 lines)

```python
OPTIONAL_EXTENSIONS = ("icf",)      # top-level packages we look for

def load_extensions(app) -> list[Extension]:
    """Import each optional extension package and let it register itself."""
```

* `ImportError` on the top-level package ⇒ silently skipped (the folder is
  gone: the normal, supported state).
* Any other exception ⇒ logged loudly and re-raised, because a *broken*
  extension is a bug, not an absence.
* Each extension exposes `register(app) -> ExtensionInfo` and gets to mount
  routers, its own `StaticFiles`, and its own Jinja loader.
* The loader keeps a small registry (`nav items`, `identity roots`) that core
  reads. Empty registry = today's behaviour, byte for byte.

Called from `app/main.py` right after `app.include_router(...)`: **two lines**.

### Seam 2 — nav + identity are registry-driven

* `app/templates/base.html`: `{% for item in extensions.nav %}<a href="{{ item.href }}">{{ item.label }}</a>{% endfor %}` — renders nothing when empty.
* `app/main.py::_wants_identity` consults `registry.identity_roots` in addition
  to `_IDENTITY_ROOTS`. **Required**, not cosmetic: `/icf` pages need
  `request.state.user_id` and `is_account`, and `base.html` reads the latter —
  today only `/api`, `/problems`, `/admin`, `/me`, `/account`, `/login`,
  `/logout`, `/random` and `/` mint an identity.

### Seam 3 — one sandbox primitive, not two copies

`app/executor/subprocess_executor.py` currently hard-codes one harness and one
payload shape. Extract the process-launch half into
`app/executor/sandbox.py`:

```python
def run_harness(files: dict[str, str], harness_path: str, payload: dict,
                limits: Limits, overall_s: float) -> tuple[dict | None, bool]:
    """Write files + payload.json into a throwaway workdir, run
    `python -I <harness> <workdir>` under the usual rlimits / own process group
    / minimal env, return (parsed result.json | None, timed_out)."""
```

`subprocess_executor.run()` becomes a thin caller — **behaviour-identical**,
`tests/test_executor.py` untouched — and `docker_executor.py` gets the
symmetrical `run_harness` (same flags, extra files copied into the bind mount).
`icf/` then reuses the *same* sandbox boundary instead of forking it.

*Alternative considered:* duplicate ~120 lines of launcher into `icf/` for zero
core changes. Rejected: two copies of the security boundary drift, and the
review burden doubles. Mandatory either way: `executor-security-reviewer` on
this change (CLAUDE.md).

### Everything else is inside `icf/`

Templates (`{% extends "base.html" %}` works via a `ChoiceLoader` appended to
the shared env in `register()`), static assets (mounted at `/icf/static`, with
its own `icf_static()` Jinja global), content, DB, scripts, tests, docs.

### Glue that must tolerate the folder's absence

| Thing | Change | Behaviour when `icf/` is gone |
|---|---|---|
| pytest | root `conftest.py` appends `icf/tests` to `config.args` when the dir exists | plain `pytest` runs core only |
| `make test` | `EXTRA_TESTS := $(wildcard icf/tests)` passed through | expands to nothing |
| mypy | `make typecheck` passes paths explicitly: `mypy app authoring $(wildcard icf)` | falls back to `files` in pyproject |
| ruff | nothing — `icf/` is linted automatically, excluded dirs unchanged | nothing |
| `make check` | new `icf-check` target, guarded by `$(wildcard icf)` | skipped |
| coverage | `source = ["app"]` stays; ICF measured separately | `fail_under = 74` unaffected |
| `.gitignore` | `icf/data/` (its DB) — already covered by `*.db` patterns | n/a |

A core test (`tests/test_extensions.py`) pins the contract: with the loader's
list emptied, the nav has no extra items, `/icf` 404s, and the app boots.

## 3. Storage: ICF gets its own database file

`icf/data/icf.db`, its own `DeclarativeBase`, its own engine (same WAL /
`busy_timeout` / `foreign_keys` pragmas as `app/db.py`), rows keyed by the core
cookie's `user_id` **string** (no cross-file FK).

Why not tables in `lootcode.db`: that file holds irreplaceable user data and
the working agreements treat it as sacred; adding — and later orphaning —
tables for a removable feature is exactly the coupling this feature is supposed
not to have. Deleting `icf/` should leave nothing behind.

**Tradeoff, accepted:** "My Progress" can't join ICF stats into the core
dashboard. ICF carries its own history page instead. (ICF attempt history *is*
user data: `icf/docs/` repeats the three-files-together backup rule.)

| Table | Holds |
|---|---|
| `icf_attempts` | id, user_id, slug, mode (`exam`/`practice`), started_at, expires_at, ended_at, status (`active`/`finished`/`expired`), highest_level_passed |
| `icf_level_state` | attempt_id, level, unlocked_at, passed_at, passed/total at best run |
| `icf_runs` | attempt_id, level, mode (`run`/`submit`), code (capped like `MAX_CODE_CHARS`), counts, runtime_ms, created_at, `late` flag |
| `icf_run_tests` | run_id, level, test name, hidden, passed, status, time_ms, message, stdout (clipped) |
| `icf_drafts` | attempt_id → latest editor buffer (autosave) |

**Problem definitions are not in the DB.** A handful of problems load from disk
into an mtime-keyed in-memory cache — no seeding, no migration, no drift.

## 4. Problem format on disk

```
icf/content/<slug>/
  meta.json              # slug, title, difficulty, theme, tags, time_cap_minutes,
                         # class_name, hidden_tests: true|false,
                         # levels: [{level, title, points, methods:[signature strings]}]
  problem.md             # shared scenario + data model + global rules
  levels/level1.md … level4.md    # per-level requirements, prose + examples
  starter/solution.py    # the template class: every method declared, bodies `pass`
  solution/solution.py   # canonical, passes all four levels (never served)
  solution/level1.py … level3.py  # OPTIONAL checkpoints — see §7
  tests/level1/{visible.py,hidden.py} … level4/…
```

### Test modules

Tests are **authored Python**, not JSON pairs — the format needs
`assertRaises`-style checks, sequence scenarios and readable failure messages,
and 40–80 cases per level is unmanageable as data.

```python
# icf/content/in-memory-database/tests/level3/visible.py
from icf_testkit import case, expect          # injected by the harness

@case("a field is alive at ts < expiry and gone at ts == expiry")
def ttl_boundary(Database):                   # the solver's class, passed in
    db = Database()
    db.set_with_ttl("1", "A", "BC", "1", "9")
    expect(db.scan_by_prefix("9", "A", "B"), "")          # 1 + 9 == 9 → dead
    ...
```

* `@case("...")` is the only registration mechanism; the docstring-ish label is
  what the UI shows for visible tests.
* `icf_testkit` (shipped as a file copied into the workdir) provides `expect`,
  `expect_raises`, `approx`, and a failure type carrying a readable diff.
* Each case runs under its own per-test `SIGALRM`, with stdout captured per
  case (reusing the run-wide `_OutputBudget` idea from `app/executor/harness.py`).
* **Trust boundary:** test modules are repo content, exactly as trusted as
  today's canonical solutions — and therefore ICF problems are **file-authored
  only**. There is no in-app ICF editor and no route that accepts test code.
  The only untrusted input is still the solver's `solution.py`, still inside the
  same sandbox.

## 5. Runner and grading

`icf/runner.py` (in-process, server side) + `icf/sandbox/icf_harness.py`
(stdlib-only, runs *inside* the sandbox, may not import `app` or `icf`).

Flow for one graded run:

1. Collect the level's test modules (`run` = current level, visible only;
   `submit` = levels 1…N, visible + hidden).
2. `sandbox.run_harness(files={solution.py, icf_testkit.py, tests/…}, payload={cases, per-case limit})`.
3. Harness imports the user's module, resolves `class_name`, then for each case:
   fresh instance handed to the case function, `SIGALRM` armed, stdout captured,
   result = `passed | failed(message) | timeout | error(short traceback)`.
4. Server maps results to level scores, writes `icf_runs` + `icf_run_tests`,
   and decides unlocking.

Scoring: each level has `points` (25 default ⇒ 100 total); level score is
`points × passed_weight / total_weight`, attempt score is the sum. The UI leads
with **"levels completed"**, which is what the format actually measures.

Failure modes are the existing ones and must behave the same way: missing
class ⇒ every case errors with one clear message, import error ⇒ same,
print-bomb ⇒ truncation notice not a dead run, infinite loop ⇒ timeout on that
case only.

## 6. HTTP surface

| Route | Purpose |
|---|---|
| `GET /icf` | Problem cards: theme, 4 levels, time cap, your best attempt; "Resume" if one is active |
| `GET /icf/{slug}` | The workspace (below) |
| `POST /api/icf/{slug}/attempts` | Start; body `{mode}` → attempt id + `expires_at` |
| `GET /api/icf/attempts/{id}` | State: level locks, remaining ms, last results |
| `POST /api/icf/attempts/{id}/run` | `{level, code}` → visible results only (fast) |
| `POST /api/icf/attempts/{id}/submit` | `{level, code}` → full results, unlock decision |
| `POST /api/icf/attempts/{id}/draft` | Editor autosave |
| `POST /api/icf/attempts/{id}/finish` | End early |
| `GET /icf/attempts/{id}/report` | "Reached level 3 in 62 min" summary |

`/icf/static` is a mount, so `static` is a reserved slug (asserted by the
content validator). Timer is server-authoritative: after `expires_at` an exam
attempt flips to `expired`; further runs are recorded and shown but marked
`late` and never advance level state.

## 7. Authoring tooling — `icf/scripts/`

* `verify_icf.py` — the ICF analogue of `scripts/verify_bank.py`, and the gate:
  1. the content spec validates (4 levels, declared methods, no reserved slug);
  2. the **starter** parses and declares exactly the advertised class + methods
     (and fails the tests, i.e. the stubs really are stubs);
  3. the **canonical** passes every level's visible *and* hidden tests;
  4. optional but recommended: level *N*'s tests **fail** against the level
     *N−1* checkpoint solution — machine proof that each level adds a real
     requirement rather than restating the last one.
* `new_icf_problem.py` — scaffold a problem directory from `meta.json` alone
  (levels, starter stubs, empty test modules).
* `make icf-check` runs `verify_icf.py`; `make check` picks it up when `icf/`
  is present.

## 8. UI

One page does the work, styled with core CSS variables plus `icf/static/icf.css`,
and reusing the existing CodeMirror bundle (`static/vendor/cm6.js`, the
`LootEditor` global) so there's no second editor stack.

```
┌───────────────────────────────────────────────────────────────────────┐
│ In-Memory Database         ⏱ 71:24 left      L1 ✅  L2 ✅  L3 ▶  L4 🔒 │
├──────────────────────────────┬────────────────────────────────────────┤
│ Overview │ L1 │ L2 │ L3 │ L4 │  class Database:                       │
│                              │      def set(self, ts, key, ...):      │
│ Level 3 — TTL expiry         │          pass                          │
│ …requirements + examples…    │                                        │
│                              │  [▶ Run visible]  [✅ Submit level 3]  │
│                              ├────────────────────────────────────────┤
│                              │ Level 1  12/12 ✅   Level 2  9/9 ✅     │
│                              │ Level 3  14/17                          │
│                              │  ✗ ttl_boundary — expected "" got "BC(1)"│
│                              │      stdout ▸                           │
│                              │  ✓ reset_on_reset_ttl        2.1 ms     │
│                              │  ✗ Hidden test 3                        │
└──────────────────────────────┴────────────────────────────────────────┘
```

* Locked level tabs show *why* they're locked and what unlocks them.
* One shared editor buffer across levels (CodeSignal semantics): the same class
  grows; autosaved to the server and to `localStorage`.
* Visible failures show the assertion message, the case label and captured
  STDOUT; hidden ones show `Hidden test k — failed` and nothing else.
* Countdown renders from the server's `expires_at`; colour shifts at 15 and 5
  minutes; expiry freezes the level pills and shows the report link.

## 9. Seed content

Authored fresh — the `icf.txt` examples are compact crib notes, not prose to
copy. Each level statement gets a real scenario, worked examples and explicit
edge-case wording.

1. **In-Memory Database** — records/fields → `SCAN`/`SCAN_BY_PREFIX` → TTL →
   backup/restore. The canonical rotation; ships first, end to end.
2. **Banking System** — accounts/transfers → `top_spenders` ranking → payments
   with 24 h cashback → merge + look-back balance (the generation-keyed history
   trap).
3. **Recipe Manager** — CRUD with case-insensitive names → search/sort → users
   and permissions → versioning with rollback-appends-a-version.

Test authoring: hand-write the boundary cases from the *specification* (TTL at
exactly `ts+ttl`, scan of a missing record, rollback name collision, merge then
recreate), then bulk-generate randomised operation sequences. Expectations for
the generated sequences come from the canonical — which means the canonical is
the oracle, with the documented trap that a canonical bug gets baked in and
then passes vacuously. Mitigation: the hand-written spec cases come first and
must pass a canonical written independently of them.

## 10. Tests for the feature itself

`icf/tests/` — fixture problems (a tiny 2-level toy under
`icf/tests/fixtures/`, never the real content) covering: passing solution,
failing assertion, missing class, syntax error, timeout, print-bomb, hidden vs
visible redaction, gating (submit L3 before L2 passes ⇒ refused), timer expiry,
draft autosave, and the content spec over every shipped problem.

Core `tests/test_extensions.py` — absence is invisible: empty registry ⇒ no nav
item, no identity root, `/icf` 404, app boots.

## 11. Phases

| # | Phase | Deliverable | Rough size |
|---|---|---|---|
| 0 | Seam | `app/extensions.py`, nav + identity hooks, glue (conftest/Makefile/mypy), `docs/extensions.md`, `tests/test_extensions.py` | ~150 lines core |
| 1 | Sandbox primitive | `app/executor/sandbox.py` extraction, both backends rewired, executor tests green, **security review** | refactor, no behaviour change |
| 2 | Package skeleton | `icf/` package: config, db, models, store, content loader + spec, `/icf` list page from disk (no grading) | medium |
| 3 | Runner | `icf_harness.py`, `icf_testkit.py`, `runner.py`, `verify_icf.py`, fixture tests, **security review** | the risky part |
| 4 | Workspace | Templates, editor page, run/submit/draft/timer APIs, gating, results rendering | largest UI chunk |
| 5 | Content #1 | In-Memory Database, 4 levels, canonical + checkpoints, exhaustive tests, green `make icf-check` | content-heavy |
| 6 | Content #2–3 + polish | Banking, Recipe, report page, practice mode, `icf/docs/`, CLAUDE.md row | content-heavy |

Phases 0–1 are core-only and land independently; after phase 3 the feature is
verifiable from the CLI without any UI; after phase 5 it is usable.

## 12. Open questions (defaults chosen, easy to flip)

1. **Is `icf/` committed?** Default yes (it's a feature of the repo). Adding
   `/icf/` to `.gitignore` makes it local-only, exactly like
   `content/problems-extended/`.
2. **Late runs after expiry:** default is *allowed but marked late and frozen*
   (practice value) rather than a hard 403.
3. **Partial-credit display:** levels-completed leads; per-test percentage is
   secondary. CodeSignal itself scores per test.
4. **Hidden tests per problem:** `hidden_tests: false` is supported, because
   some real rotations state "no hidden tests".
5. **A `/icf` entry on "My Progress":** deliberately out of scope while the
   databases are separate.
