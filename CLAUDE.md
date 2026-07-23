# CLAUDE.md

Guidance for Claude Code (and humans) working in the **lootcode** repository.
This file is loaded into context on every session — keep it accurate and short.

## What this is

lootcode is a web app for practicing coding exercises. A user picks a problem,
writes a **Python 3** solution in the browser, runs it against tests, and gets a
score. Designed to be lightweight and run on a home/LAN server.

> **Status: working V1.** Browse/filter problems, solve in-browser, run against
> all tests (visible + hidden), get scored, track solved/history. Admins can add
> problems by hand or generate them with the Claude API. See `docs/roadmap.md`.

## Stack (see docs/tech-stack.md)

Python 3 · **FastAPI** (serves both the HTML UI and the JSON API) ·
**SQLite + SQLAlchemy** · **Jinja2** templates + **CodeMirror** editor (no Node
build step) · in-process sandbox executor (**subprocess** default, **docker**
optional) · **Anthropic Claude API** for optional problem generation.

## Repository layout

| Path | What lives here |
|------|-----------------|
| `app/main.py` | FastAPI app: startup/seed, cookie identity middleware, routers. |
| `app/routers/` | `pages.py` (HTML), `submissions.py` (run API), `admin.py`. |
| `app/executor/` | Sandboxed code execution. `harness.py` runs INSIDE the sandbox. |
| `app/llm/` | Claude-API problem generation (`generator.py`); `draft_store.py` holds AI-generated problems awaiting owner review (generation never auto-saves). Prompt templates live here as `*.txt` (`hint_prompt.txt`, `help_prompt.txt`, and `problem_prompt.txt` — the self-contained "Mode A" fill-in prompt: given a statement, emit the runnable core, contract + solution + tests + hints, for both function and class/design problems). **`problem_prompt.txt` embeds the canonical tag list verbatim — keep it in sync with `app/tags.py` when the vocabulary changes.** |
| `app/problem_validation.py` | Pre-save gate shared by the manual **and** AI admin create flows: slug format+collision, structure (reuses `scripts/test_llm_output.py`, static/no-exec), canonical-tags-only, statement↔compare consistency, and the canonical passing all tests in the sandbox; plus `find_similar_problems` (duplicate nudge). Nothing is written until it passes. |
| `app/models.py` · `db.py` · `store.py` | ORM models, engine, DB operations. |
| `app/content.py` | Load/write problems to `content/problems/`. |
| `app/testgen/` | Test-strengthening engine. Machine-generates hidden cases to catch buggy *user* solutions by **coverage**, not by beating an invented wrong solution: `features.py` (structural input tokens) + `coverage.py` (canonical execution tokens) are the backbone; `mutate.py`/`candidates.py` kills are add-only universes; `select.py` set-covers the union; `shrink.py` minimizes; `generators.py`/`constraints.py` build the input pool. See `docs/test-strengthening.md`. |
| `app/templates/` · `app/static/` | Jinja2 templates, CSS, JS. |
| `content/problems/` | Problem definitions (see `specs/problem-schema.md`); optional `<slug>/assets/` holds statement figures (see `docs/problem-images.md`); `<slug>/input_validator/input_validator.py` is the per-problem `validate_input()` legal-input predicate (see `docs/input-validators.md`). |
| `content/problems-extended/` | Optional **extended** problem set — extra problems kept local (**gitignored**), seeded alongside the default set when present. A fresh clone drops these (and any collection references to them) cleanly; skipped references are reported by `seed.py` but non-fatal. See `docs/extended-problems.md`. |
| `content/collections/` | Curated, system-defined problem lists (e.g. `blind-73.json`) used as a list filter (see `docs/collections.md`). |
| `scripts/seed.py` | Load content into the DB + verify canonical solutions. |
| `scripts/generate_problem_from_statement.py` | **Mode A (fill-in) CLI:** take a problem-statement file, inject it into `app/llm/problem_prompt.txt`, and call an OpenAI-compatible endpoint (defaults to the app's `LLM_HELP_*` env) asking for **schema-constrained JSON** (`PROBLEM_SCHEMA`, consistent with the data model / `test_llm_output.py`). Emits the problem object and (unless `--no-validate`) runs it through `scripts/test_llm_output.py`. Warns if the prompt's hard-coded tag list has drifted from `app/tags.py`. See `docs/problem-generation.md`. |
| `scripts/test_llm_output.py` | Statically validate one LLM-produced problem object (from `app/llm/problem_prompt.txt`) against the core contract: pydantic schema + semantic checks (identifiers, signatures, per-test input keys / operation sequences, compare-mode shape, hints). Never executes the code. Also reused by `app/problem_validation.py`. |
| `scripts/verify_json.py` | Verify canonical solutions before importing: valid JSON + required fields + canonical passes its tests, via `run_submission`. Takes a folder of loose problem `.json` files (e.g. AI-generator output), a batch of `<slug>/generated_full_problem.json`, a single `<slug>/` dir (verifies just its `generated_full_problem.json`, ignoring the sibling `meta.json`), or a single `.json` file. |
| `scripts/verify_bank.py` | Run every problem's canonical solution against its own tests (the whole on-disk bank — **both** content roots, default + extended), via the same `run_submission` path; prints per-problem pass/fail + statistics. `--content-dir <dir>` scopes to one root; args for slug/substring filtering, `-v`/`-q` verbosity, `-j` parallelism, `--failfast`, `--strict`. |
| `scripts/import_generated_problems.py` | The bulk-import **gate** for a staging folder of **fully-generated** problems (function **or** class/design) — `<src>/<slug>/{meta.json (title+body), generated_full_problem.json (kind, contract, canonical, tests, hints, tags), assets/}`. Runs every existing gate cheapest→dearest, short-circuiting: presence/slug, **structural** (`scripts/test_llm_output.py`, strict pydantic+AST; `--strict` promotes warnings), **slug-collision** (cross-root/DB = hard skip; target-root needs `--overwrite`), **behavioral + statement↔judge consistency** (`scripts/audit.py`). Only slugs passing **all** qualify; prints a report, confirms (`--yes`), then writes each to a content root (default `content/problems-extended/`, `--out` to choose; title/body from meta.json, rest from the core via `app.content.write_problem_files`; rewrites `](assets/x)` paths, copies figures), reloads from disk, **upserts into the DB, and re-verifies from the DB**. `--dry-run`/`--slug`/`-v`. Driven by the `generated-problem-import` agent. See `docs/importing-problems.md`. |
| `scripts/strengthen_tests.py` | Batch sweep (**both content roots**): generate hidden cases that widen behavioral **coverage** of the canonical (structural + execution tokens; mutant/population kills add-only) over `app/testgen/`. `--dry-run` by default, `--apply` writes cases back. Handles **class/design (`kind: "class"`)** problems (coverage-only, sandbox-graded). See `docs/test-strengthening.md`. |
| `scripts/oracle.py` | Single-problem hardening on the same `app/testgen` engine, agent-facing: `cover` (coverage-first selection — the backbone, no adversary needed), `fuzz --solution X --shrink` (a concrete failing solution IS in hand → keep every in-domain input it fails on, shrunk to minimal reproducers; **add-only**), `suite` (does a wrong solution slip the stored suite?), `analyze` (per-input oracle table). Canonical is the only oracle; every input gated through the validator; all via `run_submission`. **Class/design (`kind: "class"`) problems supported**: generates `{operations, args}` sequences from the method signatures, coverage = op-sequence features + output signature, graded sandbox-only. |
| `scripts/check_constraint_validators.py` · `generate_constraint_validators.py` · `generate_class_validators.py` | Audit / generate the per-problem input validators (`<root>/<slug>/input_validator/input_validator.py`): every stored test input must satisfy its problem's `validate_input()`. The checker audits **both** content roots (default + extended). Function problems: `generate_constraint_validators.py` (LLM, from prose bounds). **Class/design problems: `generate_class_validators.py` — deterministic (no LLM), emits `validate_input(operations, args)` straight from the class block** (aligned lists, constructor-once-at-front, declared methods, per-arg arity/type). Run when adding test cases. See `docs/input-validators.md`. |
| `scripts/recheck_solutions.py` | Re-grade users' accepted solutions against the *current* tests, via `run_submission`. `users` lists every user + stats (submissions / solved / attempted); `check <user>` takes each solved problem's latest passing submission and re-runs it, flagging **regressions** (accepted before, fail now — the point of strengthening). Grades against the DB by default, or `--from-content` for the freshest on-disk tests (no re-seed). `-v` per-failing-test detail, `-j` parallelism. |
| `scripts/improve_hints.py` | Hint **quality gate**: a generate→judge→regenerate loop that fixes hints which give away the solution (or are too vague). `audit` grades every problem's hints against its canonical solution (local Qwen judge) → `.hints/audit.json`; `fix --from-report` regenerates only the flagged ones (`--dry-run` default, `--apply` writes, strictly-better-only) and writes a durable old→new report (`.hints/fix-dry.json`); `apply-report` writes the exact reviewed hints from that report verbatim (no regeneration — `fix --apply` re-rolls at temperature>0); `calibrate` checks the judge against `app/llm/hint_exemplars.json`. `scripts/hint_audit_report.py` / `hint_compare_report.py` render the audit and old→new reports into self-contained browsable HTML. Engine in `app/llm/hint_generator.py`. See `docs/hint-generation.md`. (`scripts/generate_hints.py` is the older one-shot, ungated seeder.) |
| `tests/` | pytest (incl. adversarial executor tests). |
| `docs/` · `specs/` · `.claude/` | Docs, content spec, Claude Code config. |

## Common commands

```bash
# Local dev env is a self-contained conda env at ./.venv (its own python
# binary + stdlib, independent of anaconda base). Recreate it with:
#   conda create -y -p ./.venv python=3.12
# Activate with `conda activate ./.venv` (conda envs have no bin/activate);
# or just call ./.venv/bin/python directly — which is what the scripts do.
.venv/bin/python -m pip install -r requirements.txt      # runtime deps
.venv/bin/python -m pip install -r requirements-dev.txt  # + pytest/httpx for tests
python scripts/seed.py                     # seed DB from content/ and verify
python scripts/audit.py                    # check statement/test/judge consistency
python scripts/build_bank.py               # (re)generate the bundled problem bank
python scripts/generate_problem_from_statement.py statement.txt -o problem.json  # Mode A: LLM fill-in from a statement
python scripts/verify_json.py test_output  # batch-verify loose problem JSON before importing
python scripts/verify_bank.py -j 8          # run every canonical solution against its tests
# Bulk-import a staging folder of fully-generated problems (function or class),
# one colocated <slug>/{meta.json, generated_full_problem.json, assets/} per problem:
python scripts/import_generated_problems.py <staging-dir> --dry-run  # validate + report every gate, write nothing
python scripts/import_generated_problems.py <staging-dir>            # ...then confirm to write + upsert the ones that qualify
python scripts/strengthen_tests.py --filter tree -j 8          # dry-run: coverage-widening hidden cases (batch)
python scripts/oracle.py cover <slug>                          # coverage-first hardening for one problem
python scripts/oracle.py fuzz <slug> --solution bad.py --shrink  # add minimal cases a known-bad solution fails
python scripts/check_constraint_validators.py                  # audit that every test input satisfies its validate_input()
uvicorn app.main:app --reload              # dev server (http://127.0.0.1:8000)
HOST=0.0.0.0 uvicorn app.main:app          # reachable on your home network
python -m pytest -q                        # run tests
```

The DB auto-creates and seeds on first startup, so `uvicorn app.main:app` alone
works for a fresh checkout.

## Conventions

- Python 3, type hints, small modules. `snake_case`; 4-space indent.
- The DB is the runtime source of truth; `content/problems/` is the durable,
  human-editable mirror (manual/AI problems are written back to it).
- Solver code defines a **top-level function** named by the problem's
  `function_name` (no class wrapper) — **unless** the problem is `kind: "class"`.
- **Design problems (`kind: "class"`):** stateful "design" problems (LRU Cache,
  Min Stack, Browser History…) where the solver implements a **class**, graded by
  replaying a method-call sequence against one instance. `meta.json` carries a
  `class` block; on the model, `params` holds the constructor params and
  `class_methods` the method signatures; tests are `input={operations, args}` →
  `expected` outputs list. The harness (`app/executor/harness.py::_run_class`)
  instantiates and dispatches. Non-deterministic (`getRandom`) and compositional
  (`serialize`↔`deserialize`) design problems are **deferred** (need a custom
  judge). A staging folder of fully-generated design problems
  (`<src>/<slug>/{meta.json, generated_full_problem.json, assets/}`) imports in
  bulk via `scripts/import_generated_problems.py` (default target
  `content/problems-extended/`), driven by the `generated-problem-import` agent.
  See `docs/design-problems.md` and `specs/problem-schema.md`.
- **Rich types:** a param/return `type` may be `TreeNode`, `ListNode` (singly-linked,
  `val`/`next`) or `DoublyLinkedList` (class `Node`, `val`/`prev`/`next`). Stored on
  disk as a plain JSON value (tree = level-order array; list = flat value array); a
  codec in `app/executor/harness.py` (`_CODECS`) builds/serializes the real object at
  the sandbox boundary and injects the class, so the judge still compares JSON. Adding
  one = a `_CODECS` entry + `executor-security-reviewer`. See `specs/problem-schema.md`.

## Working agreements for Claude

- **Security-critical:** any change under `app/executor/` (especially
  `harness.py`) or any path that runs user code must preserve the sandbox
  guarantees in `docs/code-execution.md`. Keep `tests/test_executor.py` (TLE /
  error / fork cases) green. Use the `executor-security-reviewer` subagent.
- Adding/editing a problem? Follow `specs/problem-schema.md` (format) **and**
  `specs/problem-authoring-guidelines.md` (quality bar + owner's house rules), and
  make sure the canonical solution passes all tests (`python scripts/seed.py`).
  Use `/add-problem` (one) or `/new-problem-set` (a batch); both defer to those
  specs, as does the `problem-author` subagent. The guidelines file is the single
  source of truth — its marked block is injected into the in-app AI generator's
  system prompt, so a rule added there applies to manual and AI authoring alike.
- **Tags:** use the canonical vocabulary only (39 tags). `app/tags.py` is the
  source of truth (`normalize_tags` runs on every content write); `specs/tags.md`
  is the prose taxonomy; the `canonical-tags` skill is the authoring workflow. If
  a problem fits no canonical tag, discuss adding one — don't invent it inline.
- **Statement ↔ judge consistency:** a problem's `compare` mode (meta.json) must
  match what the statement promises about answer order (`exact` / `unordered` /
  `set_of_lists`). `python scripts/audit.py` must stay green.
- **Adding test cases?** Each problem has an input-constraint validator at
  `content/problems/<slug>/input_validator/input_validator.py` exposing
  `validate_input(<params>) -> bool`. A new `(input, expected)` case's input must
  satisfy it (i.e. be in-bounds for the stated constraints) before you add it —
  run `python scripts/check_constraint_validators.py --slug <slug>`. See
  `docs/input-validators.md`. To *strengthen* a weak suite (a wrong solution
  scores full marks — the "passes here, fails on LeetCode" gap), the principle is
  **coverage keeps an input; wrong solutions only ever add cases, never veto one**
  (see `docs/test-strengthening.md`). Use the **`test-strengthener` subagent** or
  `scripts/oracle.py cover <slug>` (coverage-first) for one problem;
  `oracle.py fuzz <slug> --solution X --shrink` when a concrete failing solution is
  in hand; or the **`scripts/strengthen_tests.py`** sweep for the whole bank. All
  keep the canonical as the only oracle and gate every input through the validator.
- **LLM generation** shares one "core" output contract across modes (see
  `docs/problem-generation.md`). The **fill-in / Mode A** transform — given a
  statement, emit the core — has two front ends: a CLI
  (`scripts/generate_problem_from_statement.py <statement-file>`, prompt in
  `app/llm/problem_prompt.txt`, validated by `scripts/test_llm_output.py`) **and** the
  in-app admin **"Generate with AI"** page. `generator.generate_from_statement`
  **calls the CLI's `generate()` directly** (not a re-implementation), so the fill-in is
  byte-for-byte identical incl. the typed per-kind schema and generated hints — don't
  re-route it through the generic JSON helper (that drops the optional hints).
  The in-app page is a **one-at-a-time, two-step** flow (no batch): choice 1 turns an
  *idea* into a **statement** (`generator.generate_statement`, the one piece the CLI
  lacks); choice 2 takes a *statement* (typed or from choice 1) and, after a
  **duplicate check** (`generator.suggest_title_slug` → `find_similar_problems`, top-5),
  fills it in to a full problem (`generator.generate_from_statement`). Statements
  in flight live in `app/llm/statement_store.py`. It runs on the local OpenAI-compatible
  `LLM_HELP_*` endpoint (the CLI's default). Idea→statement / title-slug also run — Claude API
  when `ANTHROPIC_API_KEY` is set (preferred), else the OpenAI-compatible `LLM_HELP_URL`
  endpoint (`generator.active_backend()`); enabled when either is available
  (`settings.generation_enabled`). **Generation never saves directly:** the verified
  problem opens a **review page** (New-problem form, prefilled) with a slug-collision
  guard and similar-problem suggestions; the owner Creates it through the one validated
  save path (`POST /admin/new` → `app/problem_validation.py`), the same gate the manual
  and edit forms use. (The from-scratch `generator.generate_problem` remains in code but
  is no longer wired to the UI.) See `docs/problem-generation.md`.
- **Figures:** when a problem needs a diagram, follow `docs/problem-images.md`
  (when to add one, SVG how-to, and the `content/problems/<slug>/assets/` +
  `/problems/{slug}/assets/{filename}` serving API). Bulk text imports go through
  the `/bulk-import` skill, which also fixes plain-text formatting damage.
- **Hints:** up to 3 progressive hints per problem, and the last tier must **hint at
  the insight, not transcribe the solution** (no recurrence/formula/step-list). The
  quality gate is a generate→judge→regenerate loop that grades hints against the
  canonical solution — use `scripts/improve_hints.py audit`/`fix` (or the
  `generate_hints_verified` engine), not the older ungated `generate_hints.py`. Tier
  rules in `specs/problem-schema.md`; pipeline in `docs/hint-generation.md`. A
  separate **on-demand** "Get More Help with AI" button on the problem page streams
  one extra, more-revealing hint from an OpenAI-compatible LLM endpoint
  (`LLM_HELP_URL`, probed once at startup → `settings.llm_help_available`); engine in
  `app/llm/help_generator.py`, see `docs/ai-help.md`.
- Keep this file and `docs/` in sync with reality as the app grows.
