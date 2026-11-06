# Development

How to work on lootcode itself: the dev setup, the checks that gate a change,
and a map of the repository. For running the app, see the
[README](../README.md#getting-started). The working agreements (database rules,
sandbox rules, authoring rules) are in [`CLAUDE.md`](../CLAUDE.md) and
[`CONTRIBUTING.md`](../CONTRIBUTING.md).

## Setup

```bash
make install                 # ./.venv + dev deps (pinned by constraints.txt)
make hooks                   # optional: pre-commit hooks
make dev                     # uvicorn with autoreload on http://127.0.0.1:8000
```

Or by hand: `pip install -r requirements-dev.txt` inside your venv.

## Checks

```bash
make check                   # lint + types + tests + the whole bank, deduplicated and parallel (~19s)
python -m pytest -q          # tests, incl. adversarial executor (TLE / fork-bomb / error)
make test-fast               # everything except the real-sandbox tier

python scripts/check_db.py   # is lootcode.db physically intact?
python scripts/seed.py -j 8  # (re)load content into the DB and verify canonical solutions
python scripts/audit.py -j 8 # statement ↔ test ↔ judge consistency
python scripts/verify_bank.py -j 8               # run every canonical against its own tests (all roots)
python scripts/check_constraint_validators.py    # every stored test input satisfies its validate_input()
python scripts/check_math.py                     # every $…$ / $$…$$ in a statement parses in KaTeX
python scripts/verify_json.py <folder>           # batch-verify loose problem JSON before importing
python icf/scripts/verify_icf.py                 # ICF extension: every canonical passes every level
```

`verify_bank.py`, `audit.py` and `check_constraint_validators.py` cover the
whole on-disk bank — both the committed `content/problems/` and the optional
local `content/problems-extended/` set — and `--content-dir <dir>` scopes any of
them to a single root. `make help` lists every target.

## Managing problems

```bash
python scripts/find_problem.py <leetcode-url>    # is this problem already in the bank?
python scripts/generate_problem_from_statement.py statement.txt -o problem.json  # LLM fill-in from a statement
python scripts/import_generated_problems.py <staging-dir> --dry-run   # validate a staging folder, write nothing
python scripts/import_generated_problems.py <staging-dir>             # ...then import the ones that qualify
python scripts/remove_problem.py <slug> --dry-run                     # retire a problem (content + collections + DB)
python scripts/improve_hints.py audit                                 # grade every problem's hints
```

Authoring rules live in [`specs/problem-schema.md`](../specs/problem-schema.md)
and [`specs/problem-authoring-guidelines.md`](../specs/problem-authoring-guidelines.md).
See also [importing-problems.md](importing-problems.md),
[removing-problems.md](removing-problems.md),
[problem-generation.md](problem-generation.md) and
[hint-generation.md](hint-generation.md).

## What's in this repo

**The application** — everything needed to run lootcode:

| Path | What it is |
|------|------------|
| `app/` | The FastAPI app: HTML UI (`routers/pages.py`, `templates/`, `static/`), JSON run API (`routers/submissions.py`), admin (`routers/admin.py`), sandboxed `executor/` (`sandbox.py` is the shared launcher; `harness.py` runs inside the sandbox, with rich-type codecs for `TreeNode`/`ListNode`/`Node`), LLM features (`llm/`: problem generation, on-demand help, solution analysis), the extension seam (`extensions.py`), and the ORM/data layer (`models.py`, `db.py`, `store.py`, `content.py`, `tags.py`, `auth.py`, `config.py`). |
| `content/problems/` | The problem definitions (Markdown statement + tests + starter + canonical solution; optional `assets/` figures and an `input_validator/` legal-input predicate). Durable, human-editable mirror of the DB. |
| `content/problems-extended/` | Optional **extended** problem set kept local (gitignored), seeded alongside the default set when present. See [extended-problems.md](extended-problems.md). |
| `content/collections/` | Curated **collections** (`blind-73.json`, `top-interview-150.json`, `ml-coding.json`, …) used as a list filter. See [collections.md](collections.md). |
| `scripts/` | Operational scripts: DB integrity check, seed/verify, consistency audit, bank verification, input-validator audit/generation, KaTeX check, problem lookup/import/removal, hint quality gate, SVG figure helpers. |
| `authoring/` | Offline authoring tooling (the hint generate→judge→regenerate engine). Nothing in `app/` imports it. |
| `icf/` | **Optional extension**: the Industry Coding Framework — timed 4-level assessments, with its own problems, database, templates, scripts, tests and docs. Loaded at startup if the folder exists (`app/extensions.py`), invisible if it does not. See [extensions.md](extensions.md) and [`icf/README.md`](../icf/README.md). |
| `tests/`, `conftest.py` | pytest suite. The root `conftest.py` redirects every database to a temp file, so the suite never touches `lootcode.db`. |
| `docs/`, `specs/` | Engineering docs and the problem-schema / authoring / tags specs. |
| `Dockerfile`, `docker-compose.yml`, `infra/`, `Makefile`, `requirements*.txt`, `.env.example` | Build / run / deploy config. |
| `CLAUDE.md`, `CONTRIBUTING.md`, `.claude/` | Project guidance and Claude Code config (skills, subagents). |

**Problem-loading tooling** — used to *bulk-build the bank*, not needed to run the app:

| Path | What it is |
|------|------------|
| `scripts/build_bank.py` | Bulk-author pipeline. Each problem ships a canonical solution; every test's expected output is *computed* by running that canonical and cross-checked against a brute-force reference, so a buggy problem can't enter the bank. Output is written into `content/problems/`. |
| `scripts/import_generated_problems.py` | The gate for importing a staging folder of already-generated problems (function or class). See [importing-problems.md](importing-problems.md). |

## Further reading

- [architecture.md](architecture.md) · [data-model.md](data-model.md) · [api-design.md](api-design.md)
- [code-execution.md](code-execution.md) · [security.md](security.md) — the sandbox guarantees and the LAN trust boundary
- [database.md](database.md) — which tables are derived from `content/` and which hold user data that exists nowhere else
- [roadmap.md](roadmap.md) — status and what's next
