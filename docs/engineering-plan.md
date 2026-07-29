# lootcode — Engineering Hardening Program
> **Stale section warning (2026-07-29):** everything below about `testgen/`,
> `strengthen_tests.py`, `oracle.py`, `strengthen_scheduler.py`,
> `collect_candidates.py`, `export_strengthened.py` and the `test-strengthener`
> agent is obsolete — that subsystem was **deleted**. See `docs/test-strengthening.md`.


> **Status: in progress.** Findings audit + phased execution plan. Written
> 2026-07-28 against HEAD `8215128`.
>
> **Phases 0–4 are done** (2026-07-28). Phases 5–6 are still proposals.
> See [Execution log](#execution-log) at the bottom for what landed, what was
> done differently from this plan, and why.

## Context

lootcode is a working V1 (1,173 problems, 8.3k LOC in `app/`, 24.8k in `scripts/`,
1.35k in `tests/`) that grew fast and feature-first. The functionality is good; the
engineering substrate underneath it never caught up. A full read of `app/`,
`scripts/`, `tests/`, `docs/`, `specs/`, and `.claude/` found three distinct problems:

1. **Confirmed correctness bugs**, some user-visible. The biggest: figures for the
   435 extended problems 404 because `app/routers/pages.py:391` resolves assets only
   under `settings.CONTENT_DIR` — 114 extended problems have an `assets/` dir. The
   same single-root assumption in `app/routers/admin.py:63` makes editing an extended
   problem silently write a *duplicate* into `content/problems/`.
2. **A missing engineering floor.** No `pyproject.toml`, no linter, no formatter, no
   type-checker, no pre-commit, no CI that runs tests — despite 37 ruff-coded `# noqa`
   directives already written in `app/` for a ruff that isn't installed. Tests write
   to the live 21 MB dev `lootcode.db`. 22 of 33 routes have no test;
   `app/problem_validation.py` — the 479-line pre-save gate every admin write goes
   through — has zero.
3. **Documentation that has drifted far from the code.** 14 dead references, 22
   factually-wrong claims. Three docs point contributors at `services/executor`, a
   path that does not exist, including the security-review gate itself.
   `CONTRIBUTING.md` tells contributors to run `pnpm lint` in a pure-Python repo.
   `docs/test-strengthening.md` describes the *pre-rewrite* algorithm in its second
   half and the current one in its first.

**Intended outcome:** the bank, the sandbox, and the authoring pipeline keep working
exactly as they do today, but the repo becomes one a stranger (or a future agent) can
change safely — checks that run themselves, tests that don't touch live data, module
boundaries that match what the code actually does, and docs that are true.

**Decisions taken (owner, this session):**
- **Scope: full program** — bugs + tooling + docs + the structural refactor, phased.
- **Admin auth: not added.** Single-user/LAN is the accepted trust boundary. Instead:
  document it explicitly and make the app *refuse to start* on a non-loopback bind
  without an explicit opt-in.
- **Docs: rewrite to match reality.** Regenerate the wrong ones from code; move
  genuinely-unbuilt designs to `docs/proposals/` with a `Status:` header. Delete
  nothing that still has intent behind it.

---

## Deliverables

Two documents, written in Phase 0 and kept current as the program runs:

- **`docs/engineering-review.md`** — the findings: what's wrong, where, why it
  matters, with file:line citations. The durable record of this audit.
- **`docs/engineering-plan.md`** — the phased execution plan below, as a living
  checklist the owner (or an agent) works through.

---

## Phase 0 — Land what's in flight, write the program docs ✅

The working tree holds **three unrelated changes** (LLM re-check feature, topic-chip
CSS refactor, `audit.py` class-problem fix). All three look finished and consistent.

- **`git add app/static/llm_refresh.js` — it is untracked**, and
  `app/templates/admin/index.html:79` (tracked, modified) already `<script src>`s it.
  A `git commit -a` today ships the template without the script: a silent 404 and a
  dead button, because `app/templating.py:40-41` falls back to an unversioned URL on
  `OSError` rather than failing loudly.
- Commit as three commits, not one. Adopt Conventional Commits here — `CONTRIBUTING.md:8`
  already mandates it and **zero of 40 commits** follow it (half are `stuff`,
  `claude did this`, `changed stuff`).
- Write `docs/engineering-review.md` and `docs/engineering-plan.md`.

**Verify:** `git status` clean; `make test` passes; the ↻ button on `/admin` works.

---

## Phase 1 — Engineering floor ✅

The cheapest, highest-leverage phase. The suppression work for ruff is *already done*.

- **`pyproject.toml`** — project metadata + three tool sections:
  - `[tool.ruff]` line-length 88 (the de-facto house limit; only 68 lines exceed it),
    with the rule families the existing `# noqa`s already reference: `BLE001`, `N802`,
    `E402`, `A002`, `S307`, `S102`, `F401`, `ANN001`. Per-file ignores for
    `app/executor/harness.py` (stdlib-only sandbox code, deliberately minimal).
  - `[tool.mypy]` — start lenient, `app/` only, `ignore_missing_imports`. `app/` is
    already 74% return-annotated; the gap is concentrated in route handlers.
  - `[tool.pytest.ini_options]` — **`testpaths = ["tests"]`**. Today a bare `pytest`
    from the repo root imports `scripts/test_llm_output.py` at collection time (visible
    as a `PytestCollectionWarning`); it collects 0 tests now, but will break the day
    that file grows a `def test_*`.
- **`requirements-dev.txt`**: add `ruff`, `mypy`, `pytest-cov`, `pre-commit`.
- **Pin runtime deps.** `requirements.txt` is 8 packages, all `>=` floors, no lockfile
  — a fresh `pip install` today can pull a FastAPI/SQLAlchemy major that breaks the app.
  Add a `constraints.txt` (or upper bounds) captured from the known-good `.venv`.
- **`.pre-commit-config.yaml`**: `ruff check --fix`, `ruff format`, trailing-whitespace,
  end-of-file-fixer.
- **`Makefile`**: add `lint`, `format`, `typecheck`, `audit`, `verify`, and a `check`
  meta-target. Fix `run:` — it hardcodes `--host 10.8.0.1` (the owner's VPN IP) while
  `README.md:54` advertises it as the generic LAN shortcut. Use `HOST ?= 0.0.0.0`.
- **`.github/workflows/ci.yml`** — the first CI that runs anything. Install, seed,
  `pytest`, `ruff check`, `mypy`. (`claude.yml` is currently the only workflow and it
  only answers `@claude` mentions.) Note CI can only cover the default 738-problem
  root; `content/problems-extended/` is gitignored by design.
- Fix whatever ruff/mypy surface. Expected to be small.

**Verify:** `make check` green from a clean clone; CI green on a scratch PR.

---

## Phase 2 — Test foundation ✅

- **`tests/conftest.py`** — the single most important file in this program. Today
  `TestClient(app)` runs the real lifespan against `settings.DB_PATH`, i.e. the
  developer's live 21 MB `lootcode.db`. `tests/test_accounts.py:17-25` inserts real
  users and submissions into it; nothing ever deletes them;
  `tests/test_app.py:133-138` mutates the `Collection` table. Fix by setting
  `LOOTCODE_DB` to a tmp path *before* `app.config` is imported, and hoist the
  `client` fixture (currently duplicated verbatim in three test modules).
  `tests/test_jsontext_bigint.py:24-34` already does this correctly — follow it.
- Register a `slow` marker for the sandbox tier (each `run_submission` spawns a real
  subprocess; `tests/test_executor.py` + `tests/test_class_problems.py` dominate
  runtime) so `-m "not slow"` gives a fast inner loop.
- `pytest-cov` with a floor, ratcheted up per phase.
- **Cover the zero-test critical paths**, in priority order:
  `app/problem_validation.py` (479 LOC, gates every admin write), `app/tags.py`
  (`normalize_tags` runs on every content write), `app/store.py`, `app/content.py`
  (round-trip: load → write → load), `app/auth.py`.
- **Cover the untested routes** — 16 of 17 `/admin` routes have none, including
  `POST /admin/new` (the one validated save path), `POST /admin/problems/{slug}/edit`,
  `POST /admin/verify`, and all 8 `/admin/generate/*`. Also `POST /api/llm/refresh`,
  `POST /problems/{slug}/help`, `GET /random/{difficulty}`, `POST /me/name`, `GET /account`.
- **Two guard tests that make drift mechanically impossible** — these are what would
  have prevented the entire Phase 6 backlog:
  - *Tag drift*: assert the tag lists in `specs/tags.md`, `app/llm/problem_prompt.txt`,
    and `.claude/skills/canonical-tags/SKILL.md` all equal `app/tags.py::CANONICAL_TAGS`.
    All four are currently 39/39 exact — keep it that way by machine, not by hand.
  - *Dead doc references*: assert every `app/**` / `scripts/*.py` path named in
    `docs/`, `specs/`, `README.md`, `CLAUDE.md`, and `.claude/**` exists on disk.

**Verify:** `pytest` green against a tmp DB; `lootcode.db` mtime unchanged after a run.

---

## Phase 3 — Correctness & reliability ✅

Confirmed bugs, each verified by hand this session.

| # | Fix | Where |
|---|---|---|
| 1 | Asset serving resolves only `CONTENT_DIR` → **114 extended problems' figures 404**. Walk `settings.content_dirs`. | `app/routers/pages.py:391` |
| 2 | `_save` calls `write_problem_files(data)` with no `content_dir`, so editing an extended problem writes a *second copy* into `content/problems/` (which is tracked, and then shadows the original at seed time). Resolve the owning root; the parameter already exists at `app/content.py:147`. | `app/routers/admin.py:63` |
| 3 | That same write is wrapped in `except OSError: pass` — a full disk or read-only mount silently desyncs the DB from the on-disk source of truth, with no log and no user feedback. Log it and surface it. | `app/routers/admin.py:63-65` |
| 4 | `attach_user` is `async def` doing **synchronous SQLite I/O on the event loop, on every request** — the only true blocking-async violation, and it stalls the SSE streams. Make it sync or offload. | `app/main.py:49-77` |
| 5 | SQLite engine has no `journal_mode=WAL`, no `busy_timeout`, no `foreign_keys=ON`. Default rollback-journal + 0 ms busy timeout + a write on every request (#4 creates a `User` row for every crawler and 404) is the highest-probability production failure here. Add a `connect` event listener. | `app/db.py:11-15` |
| 6 | The DB session is checked out across the entire sandbox run (up to ~15 s). Grade first, then open a session to write. | `app/routers/submissions.py:34-72`; `admin.py:256`, `:400` |
| 7 | `RunBody.code` is unbounded and stored verbatim; `stdout` is capped at 4000 chars on the way *out* but stored uncapped. Bound both. | `app/routers/submissions.py:21-22`, `:60` |
| 8 | Guest `User` rows are created for every request without a valid cookie, including bots and 404s, forever. Don't mint identity for non-page requests. | `app/main.py:56-65` |

**Logging.** `app/store.py:25` is the only logger in 8,346 lines, used at one site, and
there is no `basicConfig`/`dictConfig` anywhere. Add `app/logging_config.py` and wire
it in `lifespan`. Log at minimum: sandbox failures, DB errors, LLM failures, the #3
disk-mirror failure, and every admin write (there is currently **no audit trail** for a
bank that unauthenticated routes can overwrite).

**LAN trust boundary** (per owner decision — no auth added):
- State the trust model plainly in `docs/security.md`: `/admin/*` is unauthenticated,
  `POST /admin/verify` (`app/routers/admin.py:384`) executes arbitrary submitted Python,
  and the default subprocess backend **does not block network access**
  (`app/executor/subprocess_executor.py:8-10`). The security boundary is the network.
- **Fail loudly**: refuse to start when bound to a non-loopback host unless
  `LOOTCODE_TRUST_LAN=1` is set. Cheap, and it converts a silent exposure into a
  deliberate one.
- `POST /api/llm/refresh` (`app/routers/submissions.py:107`) lets any visitor flip the
  process-wide `settings.llm_help_available` flag — which `settings.generation_enabled`
  reads (`app/config.py:79-84`), gating the admin LLM routes. Rate-limit it and note it.

**Verify:** load an extended problem with a figure in a browser; edit it in `/admin` and
confirm no new dir appears under `content/problems/`; `make check`; `tests/test_executor.py` green.

---

## Phase 4 — Structural refactor ✅

Move domain logic out of HTTP handlers; collapse the copies; make the layering honest.

**Extract from `app/routers/pages.py` (755 lines, ~370 of them domain logic):**
- `app/progress.py` — `_unsolved_counts`, `_topic_counts`, `_topic_cloud`,
  `_first_solved`, `_blocks_by_local_date`, `_lay_out_week`, `_weekly_streak`,
  `_month_calendar` (`pages.py:124-336`). Pure functions with zero HTTP dependency —
  currently untestable in place, trivially testable once moved.
- `app/pagination.py` — `_page_window`, already being imported *across routers as a
  private* (`app/routers/admin.py:34`).
- `app/provided_types.py` — `PROVIDED_TYPE_DEFS` (`pages.py:30-68`), which duplicates
  the harness's class definitions **as strings** (`app/executor/harness.py:62-258`).
  One source, both readers.

**Split `app/routers/admin.py` (758 lines, 4 responsibilities):**
`admin_problems.py` (CRUD) + `admin_generate.py` (the ~290-line AI flow, near-zero
coupling to the rest) + `admin_forms.py` (marshalling — the same 14-key form structure
is hand-listed **five** times: `_form_view`, `_data_to_form`, `_blank_form`,
`_raw_form`, and `edit_submit`'s `typed` dict).

**Collapse the duplication:**
- `app/llm/client.py` — one OpenAI/Anthropic transport. Today the client construction
  is copied 4× (`help_generator.py:53`, `hint_generator.py:106`, `generator.py:253`,
  `testgen/candidates.py:102`) with four different timeout policies;
  `_loads_loose` 2×; the `response_format` degradation ladder 3×.
- **Kill the four hand-rolled "problem-like" shims** (`admin.py:350`,
  `problem_validation.py:447`, `generator.py:166`, `generator.py:361`) in favour of
  the existing `app/executor/__init__.py:74-114` `ProblemView`/`problem_view`, whose
  docstring says it exists precisely so callers never hand-pick a subset. This also
  fixes a latent bug: `generator.py:166`'s `_ProblemLike` omits
  `kind`/`class_name`/`class_methods`, so it silently cannot grade class problems.
- Frontend: `app/static/sse.js` for the SSE reader loop that is **byte-identical in
  three files** (`app.js:246-269`, `generate.js:48-75`, `generate_statement.js:119-146`),
  plus the identical error preamble and progress-bar machinery. Extract the
  character-identical kind-toggle IIFE from `admin/new.html:153-169` and
  `admin/edit.html:79-95`.

**Fix the layering (the two inverted dependencies):**
- **`app/` imports from `scripts/` by mutating `sys.path` at import time** —
  `app/problem_validation.py:63-66` and `app/llm/generator.py:473-483`, both in the
  request path. Make the shared pieces (`test_llm_output`'s schema,
  `generate_problem_from_statement.generate`) a real importable package that both
  `app/` and `scripts/` depend on, so the arrow points one way.
- **Move the offline tooling out of the runtime package.** `app/testgen/` (2,393 LOC)
  and `app/llm/hint_generator.py` (548 LOC) have **no importer anywhere in `app/`** —
  35% of the runtime package's Python is authoring tooling. Move to a top-level
  `authoring/` package. This makes the Docker image smaller, the runtime dependency
  set honest, and the boundary self-documenting. Update `scripts/oracle.py`,
  `strengthen_tests.py`, `collect_candidates.py`, `export_strengthened.py`,
  `improve_hints.py`, `tests/test_testgen.py`, and the `CLAUDE.md` layout table.

Optionally split `app/testgen/generators.py` (1,150 lines; `generate_candidates` alone
is a 296-line function — the largest in the repo) into `scalars`/`expressions`/`opseq`/`domains`.
Leave `app/executor/harness.py` alone: it must stay a single stdlib-only file because
`docker_executor.py:32` copies it into the container.

**Verify after each extraction:** `make check` + `scripts/verify_bank.py -j 8`. The
extractions are mechanical; the test suite from Phase 2 is what makes them safe.

---

## Phase 5 — `scripts/` consolidation & repo hygiene _(not started)_

`scripts/` is 24.8k LOC, is **not a package**, has no shared library, and uses two
mutually-incompatible import conventions (18 files `sys.path.insert` the repo root;
`export_strengthened.py:65` uses `from scripts.…`; two files put `scripts/` itself on
the path and bare-`import` a sibling).

- **`scripts/__init__.py` + `scripts/_common.py`**: `iter_problem_dirs` (4 copies —
  and 2 of them, `generate_hints.py:45` and `generate_constraint_validators.py:514`,
  are silently single-root and lack the missing-root guard); `Palette` (2 verbatim
  copies); LLM `preflight` (3 copies + the app's own `probe_endpoint`); `_client`; a
  shared argparse parent for the `--base-url/--model/--api-key/--slug/-j/--dry-run/-v/-q`
  flags that 18 scripts each hand-roll.
- **`make check` / `scripts/check_all.py`** — one entrypoint chaining `pytest` → `seed`
  → `audit` → `verify_bank` → `check_constraint_validators`. Today that's a five-line
  block a human copies out of `README.md:62-66`.
- **Fix `scripts/audit.py:144-145`**: it seeds only `if not db.query(Problem).count()`,
  so on any developer machine it silently audits **stale DB content** rather than what's
  on disk. `verify_bank.py` reads `content.load_all_roots()` directly and does not have
  this bug — make `audit.py` match.
- Retire the dead: `find_duplicate_slugs.py` (257 LOC, **0 references** anywhere) and
  `seed_one.py` (**0 references**). Decide `generate_hints.py`'s fate — `CLAUDE.md:176`
  already says use `improve_hints.py` instead.
- **Hygiene**: `.gitignore` (or stop generating) the ~738 `content/**/__pycache__` dirs
  that `check_constraint_validators.py` creates inside the content tree — they make
  `git status --ignored` unusable. Clean `staging/` (22 MB, 500 dirs), `.hints/`
  (1.2 MB of un-rotated timestamped backups), `constraint_validators/` (964 KB, stale,
  superseded by the 738 in-tree validators), `scratchpad/`, the root `__pycache__` of
  deleted scratch modules, and the personal `resume.txt` sitting in the repo root.

**Verify:** every script still runs (`--help` smoke test); `make check` green.

---

## Phase 6 — Documentation revamp _(not started)_

26 markdown files, 14 dead references, 22 factually-wrong claims. Ordered by blast radius.

**6a — Wrong in the security path (do first).**
- `services/executor` → `app/executor/` in four places: `docs/code-execution.md:3`,
  `docs/security.md:39`, `CONTRIBUTING.md:20`, and
  `.claude/agents/executor-security-reviewer.md:3` — the last is the agent's
  `description:`, i.e. the text used to decide whether to invoke it at all.
- `EXECUTOR_TIME_LIMIT_MS` / `_MEMORY_LIMIT_MB` / `_MAX_OUTPUT_KB` →
  `EXEC_*` (`docs/code-execution.md:25,26,29`; real names at `app/config.py:44-46`).
- Delete `docs/code-execution.md:92-103` — a "pick one: Judge0 / Piston / e2b …
  **Recommendation for v1: start with Judge0**" block still sitting inside the
  security-critical doc, seven months after the executor was built.
- Reframe `docs/code-execution.md:14-33`: the four "MUST" guarantees are all violated
  by the shipped default backend, as the same file admits at `:42-43`. Split into
  *guarantee* vs *what `subprocess` actually gives you*.
- Remove the "must pass in CI" claims (`code-execution.md:110`, `security.md:24`) or
  make them true — Phase 1 makes them true.

**6b — Wrong in the first-run path.**
- **`HOST=0.0.0.0 uvicorn app.main:app` does not work** — verified: uvicorn's CLI uses
  the `UVICORN_*` envvar prefix, and `settings.HOST` is only read by
  `python -m app.main` (`app/main.py:88`). Wrong in three places:
  `README.md:45`, `CLAUDE.md:78`, `docs/tech-stack.md:14`.
- Resolve the setup contradiction: `README.md:33` says `python3 -m venv .venv`,
  `CLAUDE.md:56-60` says conda-at-`./.venv`. Pick one, state it once.
- **Rewrite `CONTRIBUTING.md`** — its one actionable instruction is
  "`pnpm typecheck`, `pnpm lint`, `pnpm test`" in a repo with no Node.
- Fix counts: 741 → 738 default / 435 extended / 1,173 total (`README.md` ×5,
  `docs/hint-generation.md:91`); 38 → **39** tags (`README.md:17` is the lone straggler).
- Fix `README.md:70-73` — only `verify_bank.py` has `--content-dir`; `audit.py` has no
  argparse at all. And `README.md:94` names `scripts/bank_new_p/`, which doesn't exist.

**6c — Structurally wrong docs.**
- Regenerate **`docs/api-design.md`** from `app/routers/*` — its entire `/api/v1/…`
  surface is fictional. Regenerate **`docs/data-model.md`** from `app/models.py` — it
  documents camelCase columns and two entities (`Language`, `Starter`) that don't exist.
- Move `docs/duplicate-detection-plan.md` → `docs/proposals/` with `Status: proposal`.
- **Rewrite `docs/roadmap.md`** — six weeks stale, and both `README.md:25` and
  `CLAUDE.md:14` point at it as the status source. It marks pagination and bank-growth
  as TODO (both shipped) and omits *everything* shipped since: hints + quality gate,
  the test-strengthening engine, collections, class/design problems, input validators,
  on-demand AI help, the extended root, rich types, known/visit-later.
- **Reconcile `docs/test-strengthening.md` with itself**: `:9-48` describes the
  coverage-first model; `:194-247` still describes the pre-rewrite "greedily select
  cases that kill the discriminators" algorithm verbatim. Delete the second version.
- Resolve three doc-vs-doc contradictions: `strengthen_tests.py`'s extended-awareness
  (`extended-problems.md:53-56` says it isn't; `strengthen_tests.py:867` calls
  `load_all_roots`); `verify_json.py`'s layout support (`problem-generation.md:186-188`
  vs the correct `CLAUDE.md:42`); `hint-generation.md:76`'s model id (`qwen36` vs the
  code default `local-model`).
- Update `docs/tech-stack.md` (still says "no passwords" post-accounts-V2; never
  mentions the OpenAI-compatible backend) and `docs/architecture.md` (component
  diagram predates `testgen`, `tags`, `auth`, `problem_validation`, collections, SSE).

**6d — `.claude/` agents & skills (these silently corrupt authoring output).**
- `.claude/skills/bulk-import/SKILL.md:30-34` instructs the agent to **skip class/design
  problems** — 88 exist and they've been first-class since commit `3cd8f44`.
- `:29` — its duplicate check misses `content/problems-extended/` (435 problems,
  gitignored and therefore invisible to `git grep`) and the DB.
- `:65-70` routes authoring through the 15.6k-line `scripts/build_bank.py` monolith
  instead of the modern content-dir / `import_generated_problems.py` path.
- `:39` — dangling `[the memory on import cleanup]` link with no target.
- `.claude/agents/problem-author.md:25` says "reuse existing tags", contradicting the
  canonical-vocabulary rule in `CLAUDE.md:125-128`; `:22` mentions per-language starters
  in a Python-only app.
- `add-problem`, `new-problem-set`, and `problem-author` all omit `input_validator/`
  and `hints` from their required-pieces lists, though `specs/problem-schema.md:26-27`
  makes the validator mandatory.
- `.claude/commands/plan-feature.md:10-11` cites `docs/data-model.md` and
  `docs/api-design.md` — the two least accurate docs in the repo (fixed in 6c).
- `docs/test-strengthen-scheduler.md:109` claims a `guard-outside-project.py` hook is
  the safety net for `--dangerously-skip-permissions`. `.claude/settings.json` has **no
  `hooks` key at all**. Either wire the hook or drop the claim — do not leave a stated
  safety net that isn't there.

**6e — `specs/`.**
- `specs/problem-authoring-guidelines.md:103-106`: a literal
  `**TODO(owner):** add your requirements here` plus two
  `_(example — keep or replace)_` placeholders sit **inside** the
  `AI-GUIDELINES:START/END` block that `app/llm/generator.py:141-157` injects verbatim
  into the generator's system prompt. Every AI-generated problem is being authored
  against a TODO.
- Same file `:69-75` documents only `TreeNode` under the solver contract —
  `ListNode` and `DoublyLinkedList` are missing, so the injected guidelines never
  mention two of the three rich types.
- `specs/problem-schema.md` never states the 6–10 test-case count that
  `app/llm/problem_prompt.txt:109` and the guidelines both mandate (and that
  `scripts/test_llm_output.py:221` enforces as `min_length=1`). Three sources, three rules.

**6f — What's missing entirely.**
- `docs/README.md` index + a `Status: normative | reference | proposal | historical`
  header on all 26 docs, so a reader can tell `importing-problems.md` (normative) from
  `api-design.md` (aspirational) without reading both.
- An **env-var reference** — `.env.example` exists but no doc enumerates
  `LLM_GEN_BACKEND`, `LLM_HELP_*`, `EXEC_*`, `LOOTCODE_DB`, `EXEC_DOCKER_IMAGE`.
- An **end-to-end lifecycle doc**: startup/seed → identity middleware → list filtering
  → problem render → run → grade → persist → progress; plus the content→DB→content
  round trip (`load_all_roots` → `seed_from_content` → `upsert_problem` → admin edit →
  `write_problem_files` → `normalize_tags`/`normalize_hints`). Nothing documents either.
- A `tests/` guide (what each file covers, how to add one).
- The four **ADRs** `docs/adr/README.md:12-17` has been asking for since day one
  (executor build-vs-buy, source of truth, backend framework, scoring model). All four
  decisions are made and recorded as resolved in `docs/tech-stack.md:20-32`.
- `CHANGELOG.md`, and a commit-message convention that is actually followed.
- Undocumented anywhere: `app/templating.py`, `app/auth.py`, `app/config.py`,
  the front-end JS modules, the `known`/`visit-later` filters, `GET /random/{difficulty}`,
  and the subtle `JSONText` SQLite big-int affinity workaround (`app/models.py:180-183`)
  that has a dedicated test file and no prose.

Finally: collapse the **three divergent copies of the repo-layout table**
(`CLAUDE.md:25-51`, `README.md:79-95`, `docs/architecture.md:9-34`) to one source with
pointers, and refresh `CLAUDE.md` for the Phase 4 moves.

**Verify:** the Phase 2 dead-reference guard test passes; a fresh-clone walkthrough of
`README.md` → `CONTRIBUTING.md` → `make check` works verbatim.

---

## Sequencing & risk

Run in order — each phase is independently shippable and each depends on the one before.

| Phase | Risk | Why this order |
|---|---|---|
| 0 Land in-flight | none | Clean tree before touching anything. |
| 1 Tooling | very low | Additive. Nothing behavioural. Gives every later phase a green/red signal. |
| 2 Tests | low | Additive, but **must precede Phase 4** — the refactor is only safe with it. Also stops tests corrupting the dev DB. |
| 3 Bug fixes | medium | Real behaviour changes. Small and individually verifiable; Phase 2 covers them. |
| 4 Refactor | medium-high | Large but mechanical. Do one extraction per commit, `make check` between each. |
| 5 Scripts | low | Isolated from the running app. |
| 6 Docs | none | Last, so it describes the end state rather than a moving target. |

Phases 5 and 6 can run in parallel with 4 if desired; 6d/6e (the agent, skill, and
prompt-injection fixes) are cheap and high-value and could be pulled forward.

## Verification (whole program)

1. `make check` — lint, types, tests, seed, audit, verify_bank, validators — green from a clean clone.
2. `python scripts/verify_bank.py -j 8` — every canonical still passes its own tests, both roots.
3. `python scripts/check_constraint_validators.py` — 738/738 validators still satisfied.
4. Manual pass in a browser: list + filters + pagination, solve and score a problem,
   **open an extended problem with a figure** (Phase 3 #1), edit it via `/admin` and
   confirm no duplicate dir appears under `content/problems/` (Phase 3 #2), progress page,
   AI help, admin generate flow.
5. CI green on a PR.

---

## Execution log

### Phases 0–3 — landed 2026-07-28

Twelve commits, `8215128..bc77f7e`. `make check` (lint → types → tests → seed →
audit → verify_bank → validators) is green end to end: **275 tests**, coverage
**55% → 78%**, 1,173 canonicals passing 16,338 test cases, 1,173/1,173 validators
satisfied.

| Phase | Commits |
|---|---|
| 0 | `98fd045` `aadc1f5` `f638db3` `75b7a66` |
| 1 | `7964078` `ad81162` |
| 2 | `ba24359` `f80bfb0` `edd9ec4` |
| 3 | `1f2ca09` `ffb7e11` `666d68b` `cd021bd` `bc77f7e` |

### Where execution differed from the plan, and why

- **`ruff format` is opt-in, not automated.** The plan put it in pre-commit.
  Running it today rewrites **3,174 lines in `app/` alone** — ~38% of the runtime
  package, most of it hand-aligned deliberately — and would destroy `git blame`
  immediately before Phase 4, which depends on it. It is `make format`; the
  enforced gate is `ruff check` (which still fixes import order).
- **`ANN001` and `PLC0415` are not enabled.** The plan listed `ANN001` among the
  rule families to select. It has **865 violations**, and `PLC0415`
  (import-outside-top-level) has 137 — where lazy imports are a deliberate
  pattern here (optional LLM deps, circular-import breaks). Enabling either would
  mean a thousand suppressions or a separate annotation project. The existing
  `# noqa: ANN001` / `# noqa: PLC0415` directives stay as the record of intent,
  and `RUF100` is off so its autofix cannot delete their written rationale.
- **E501 errors at 100, not 88.** `line-length = 88` still drives the formatter,
  but `app/` has only **3** lines over 100 versus 61 over 88; reflowing 300-odd
  prose comments across the repo buys nothing.
- **`app/testgen/` is excluded from mypy** rather than annotated: 21 errors, all
  `ast`/`Any` juggling, in a package nothing in `app/` imports and that Phase 4
  moves to `authoring/` anyway. Annotate it there.
- **`scripts/` has a per-file ignore list.** It is linted for real bugs but not
  style (321 long lines, 24.8k LOC). Phase 5 should shrink that list to nothing.
- **Two items were pulled forward from Phase 6**, both because they sit in the
  security path and cost one word each: the four `services/executor` references
  (6a) — including `.claude/agents/executor-security-reviewer.md`'s
  `description:`, i.e. its selection trigger — and the two dead references the
  new guard test found (`scripts/bank_new_p/`, `app/dedup.py`).

### Found during execution, not in the audit

- **`load_all_roots` does not de-duplicate.** A slug present in both content
  roots is returned twice, and the *extended* copy is the one that survives
  `upsert_problem`. This is the other half of the admin-edit bug and is now
  pinned by a test that names it as a hazard rather than an endorsement.
- **A `startswith("/admin")` prefix check also matches `/admin.php`.** The first
  cut of the identity-minting fix still created a user row for that. Caught by
  pointing scanner paths at a running server — not by the unit test, which used
  `/wp-login.php`. The check is now segment-wise.
- **`store.merge_guest_into_account` reused one loop variable** for both
  `KnownProblem` and `VisitLaterProblem` rows (found by mypy).
- **`build_bank.py`'s `_lb_brute_filedup` shadowed the imported `content`
  module** with a loop variable (found by ruff).

### Deferred, with reasons

- **`.env.example` was not updated** with `LOOTCODE_TRUST_LAN` / `LOG_LEVEL` — a
  permission guard blocks writing it. `docs/security.md` documents both. The
  env-var reference in Phase 6f should sweep this up.
- **CI has not run.** `.github/workflows/ci.yml` is committed but unproven until
  a push; every step in it was run locally and is green.
- **The coverage floor is 74%** against an actual 78%. Raise it as phases land.

### Notes for Phase 4

- `app/logging_config.py` is new and is imported by `main`, `admin` and
  `submissions`. Fold the remaining `print`-style reporting into it.
- `submissions.run` no longer takes `Depends(get_db)`; it opens two short
  sessions around the grade. `admin.py:256` and `:400` still hold a session
  across a sandbox run and should get the same treatment.
- `_owning_root` in `admin.py` is a content-layer concern living in a router —
  a candidate to move alongside the `app/pagination.py` / `app/progress.py`
  extractions.

### Phase 4 — landed 2026-07-28

Nine commits, `1695727..fa96f2b`, one extraction each, `make check` between.
`app/routers/pages.py` 763 → 464 lines; `admin.py` 809 → 35 (a mount point over
three modules); **275 → 384 tests**. The bank is untouched: 1,173 canonicals
over 16,338 test cases, 1,173/1,173 validators.

| Commit | What moved |
|---|---|
| `7c126f4` | `app/pagination.py` |
| `9090d35` | `app/progress.py` + `tests/test_progress.py` |
| `5bd04b1` | `app/provided_types.py` + `tests/test_provided_types.py` |
| `1d9c2ac` | `admin_problems` / `admin_generate` / `admin_forms` |
| `a2d903a` | `CaseView`/`case_views` next to `ProblemView`; four shims gone |
| `c12dca6` | `app/llm/client.py` + `tests/test_llm_client.py` |
| `e35b49f` | `app/static/sse.js` + `tests/test_static_assets.py` |
| `a6de5fe` | `app/problem_spec.py`, `app/llm/fill_in.py` — the layering fix |
| `fa96f2b` | `authoring/` |

### Where Phase 4 differed from the plan, and why

- **The provided-type defs are rendered from the harness, not merely moved.**
  The plan said "one source, both readers", but the harness cannot import from
  `app` — it is stdlib-only and gets copied into the container as one file. So
  the arrow points the other way: `app/provided_types.py` reads the real classes
  via `inspect`, so class names, constructor parameters and defaults, and method
  names are derived. Only prose and return annotations are authored, and a test
  pins those. Output is byte-identical bar one misaligned comment.
- **The form consolidation went further than the plan's five copies.** Using a
  pydantic model as the request body removed the two handler signatures as well.
  Worth knowing: FastAPI flattens a form model into the body only when it is the
  *sole* body parameter, so `source`/`draft_id` had to become fields of a
  subclass rather than extra `Form(...)` arguments — otherwise every field has to
  arrive nested under `form`, i.e. a 422 for the browser posting a flat form.
- **The test-case shims were killed too.** The plan named the four *problem*
  shims; the same four callers each had a test-case shim beside it, guessing
  differently at a missing `weight` or `name`. `CaseView`/`case_views` is the
  counterpart to `ProblemView`/`problem_view`. Named `CaseView` because pytest
  collects anything called `Test*` — the ORM's `TestResult` already needs an
  import alias in the suite for that.
- **`generators.py` was not split.** The plan listed it as optional; it is 1,150
  lines that nothing else in the phase depends on, and splitting it would have
  been the one change in Phase 4 with no test to hold it.
- **`_owning_root` moved to `app/content.py`** as the Phase 3 notes suggested,
  and the backend display label moved next to `active_backend()`.

### Found during Phase 4, not in the audit

- **`llm.generator` could not grade a class problem at all.** `_ProblemLike`
  omitted `kind`/`class_name`/`class_methods`, so a class/design draft was
  graded as a function problem and every test failed with "must define a
  function named ''". The audit predicted a latent bug here; this is it, and it
  is now pinned by a test.
- **`scripts/generate_problem_from_statement.py` held a fifth copy of the
  OpenAI-client construction and a third `_loads_loose`** — invisible from
  `app/`, found only when the code moved into it.
- **`scripts/generate_constraint_validators.py` broke silently** two commits
  into the phase: it imported `_loads_loose` from the hint generator, which the
  client consolidation had removed. Nothing in `make check` imports that script.
  Phase 5's `--help` smoke test over every script would have caught it same-day;
  it is worth pulling forward.
- **The Phase 2 guard tests earned their keep.** The dead-reference guard failed
  the build with the exact list of stale doc paths when `authoring/` landed.

### Notes for Phase 5

- `scripts/build_bank.py` imports `scripts.bank_new_p`, which does not exist —
  the script has been unrunnable for some time. Verified pre-existing.
- Every other script in `scripts/` now imports cleanly. Add the `--help` smoke
  test as a real test, not a manual step.
- `scripts/verify_json.py::grade` is now the last hand-rolled problem/test shim
  in the repo; `run_submission` normalizes what it builds.
- The per-file ruff ignore list for `scripts/` is unchanged and still large.
