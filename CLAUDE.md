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
| `app/llm/` | Claude-API problem generation (`generator.py`). |
| `app/models.py` · `db.py` · `store.py` | ORM models, engine, DB operations. |
| `app/content.py` | Load/write problems to `content/problems/`. |
| `app/testgen/` | Test-strengthening engine. Machine-generates hidden cases to catch buggy *user* solutions by **coverage**, not by beating an invented wrong solution: `features.py` (structural input tokens) + `coverage.py` (canonical execution tokens) are the backbone; `mutate.py`/`candidates.py` kills are add-only universes; `select.py` set-covers the union; `shrink.py` minimizes; `generators.py`/`constraints.py` build the input pool. See `docs/test-strengthening.md`. |
| `app/templates/` · `app/static/` | Jinja2 templates, CSS, JS. |
| `content/problems/` | Problem definitions (see `specs/problem-schema.md`); optional `<slug>/assets/` holds statement figures (see `docs/problem-images.md`); `<slug>/input_validator/input_validator.py` is the per-problem `validate_input()` legal-input predicate (see `docs/input-validators.md`). |
| `content/problems-extended/` | Optional **extended** problem set — extra problems kept local (**gitignored**), seeded alongside the default set when present. A fresh clone drops these (and any collection references to them) cleanly; skipped references are reported by `seed.py` but non-fatal. See `docs/extended-problems.md`. |
| `content/collections/` | Curated, system-defined problem lists (e.g. `blind-73.json`) used as a list filter (see `docs/collections.md`). |
| `scripts/seed.py` | Load content into the DB + verify canonical solutions. |
| `scripts/verify_json.py` | Batch-verify a folder of loose problem `.json` files (e.g. AI-generator output) before importing: valid JSON + required fields + canonical passes its tests, via `run_submission`. |
| `scripts/verify_bank.py` | Run every problem's canonical solution against its own tests (the whole on-disk bank — **both** content roots, default + extended), via the same `run_submission` path; prints per-problem pass/fail + statistics. `--content-dir <dir>` scopes to one root; args for slug/substring filtering, `-v`/`-q` verbosity, `-j` parallelism, `--failfast`, `--strict`. |
| `scripts/import_collection.py` | Validate + bulk-import a staged `statements/`+`rest/` collection dir (e.g. `user_collection/`) into `content/` and the DB. Runs every existing gate (structural, sandbox behavioral, statement↔judge, slug-collision), imports only what passes, copies figures, carries hints. See `docs/importing-collections.md`. |
| `scripts/strengthen_tests.py` | Batch sweep: generate hidden cases that widen behavioral **coverage** of the canonical (structural + execution tokens; mutant/population kills add-only) over `app/testgen/`. `--dry-run` by default, `--apply` writes cases back. See `docs/test-strengthening.md`. |
| `scripts/oracle.py` | Single-problem hardening on the same `app/testgen` engine, agent-facing: `cover` (coverage-first selection — the backbone, no adversary needed), `fuzz --solution X --shrink` (a concrete failing solution IS in hand → keep every in-domain input it fails on, shrunk to minimal reproducers; **add-only**), `suite` (does a wrong solution slip the stored suite?), `analyze` (per-input oracle table). Canonical is the only oracle; every input gated through the validator; all via `run_submission`. |
| `scripts/check_constraint_validators.py` · `generate_constraint_validators.py` | Audit / (LLM-)generate the per-problem input validators (`<root>/<slug>/input_validator/input_validator.py`): every stored test input must satisfy its problem's `validate_input()`. The checker audits **both** content roots (default + extended). Run it when adding test cases. See `docs/input-validators.md`. |
| `scripts/recheck_solutions.py` | Re-grade users' accepted solutions against the *current* tests, via `run_submission`. `users` lists every user + stats (submissions / solved / attempted); `check <user>` takes each solved problem's latest passing submission and re-runs it, flagging **regressions** (accepted before, fail now — the point of strengthening). Grades against the DB by default, or `--from-content` for the freshest on-disk tests (no re-seed). `-v` per-failing-test detail, `-j` parallelism. |
| `scripts/improve_hints.py` | Hint **quality gate**: a generate→judge→regenerate loop that fixes hints which give away the solution (or are too vague). `audit` grades every problem's hints against its canonical solution (local Qwen judge) → `.hints/audit.json`; `fix --from-report` regenerates only the flagged ones (`--dry-run` default, `--apply` writes, strictly-better-only) and writes a durable old→new report (`.hints/fix-dry.json`); `apply-report` writes the exact reviewed hints from that report verbatim (no regeneration — `fix --apply` re-rolls at temperature>0); `calibrate` checks the judge against `app/llm/hint_exemplars.json`. `scripts/hint_audit_report.py` / `hint_compare_report.py` render the audit and old→new reports into self-contained browsable HTML. Engine in `app/llm/hint_generator.py`. See `docs/hint-generation.md`. (`scripts/generate_hints.py` is the older one-shot, ungated seeder.) |
| `tests/` | pytest (incl. adversarial executor tests). |
| `docs/` · `specs/` · `.claude/` | Docs, content spec, Claude Code config. |

## Common commands

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt           # runtime deps
pip install -r requirements-dev.txt       # + pytest/httpx for tests
python scripts/seed.py                     # seed DB from content/ and verify
python scripts/audit.py                    # check statement/test/judge consistency
python scripts/build_bank.py               # (re)generate the bundled problem bank
python scripts/verify_json.py test_output  # batch-verify loose problem JSON before importing
python scripts/verify_bank.py -j 8          # run every canonical solution against its tests
python scripts/import_collection.py user_collection --dry-run  # validate a staged collection (statements/+rest/)
python scripts/import_collection.py user_collection            # ...then import the ones that pass every gate
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
  `function_name` (no class wrapper).
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
- **Tags:** use the canonical vocabulary only (38 tags). `app/tags.py` is the
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
- **LLM generation** comes in three modes depending on what's already given —
  fill-in (full statement / description-only) vs. from-scratch — sharing one
  "core" output contract. See `docs/problem-generation.md`. The in-app
  "Auto-generate with AI" admin feature is the from-scratch mode
  (`app/llm/generator.py`). It runs on either backend — the Claude API when
  `ANTHROPIC_API_KEY` is set (preferred), otherwise the same OpenAI-compatible
  `LLM_HELP_URL` endpoint the AI-help button uses (`generator.active_backend()`);
  the button is enabled when either is available (`settings.generation_enabled`).
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
