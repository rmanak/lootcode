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
| `app/templates/` · `app/static/` | Jinja2 templates, CSS, JS. |
| `content/problems/` | Problem definitions (see `specs/problem-schema.md`); optional `<slug>/assets/` holds statement figures (see `docs/problem-images.md`). |
| `content/collections/` | Curated, system-defined problem lists (e.g. `blind-73.json`) used as a list filter (see `docs/collections.md`). |
| `scripts/seed.py` | Load content into the DB + verify canonical solutions. |
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
- **Tags:** use the canonical vocabulary only (37 tags). `app/tags.py` is the
  source of truth (`normalize_tags` runs on every content write); `specs/tags.md`
  is the prose taxonomy; the `canonical-tags` skill is the authoring workflow. If
  a problem fits no canonical tag, discuss adding one — don't invent it inline.
- **Statement ↔ judge consistency:** a problem's `compare` mode (meta.json) must
  match what the statement promises about answer order (`exact` / `unordered` /
  `set_of_lists`). `python scripts/audit.py` must stay green.
- **LLM generation** comes in three modes depending on what's already given —
  fill-in (full statement / description-only) vs. from-scratch — sharing one
  "core" output contract. See `docs/problem-generation.md`. The in-app
  "Auto-generate with AI" admin feature is the from-scratch mode
  (`app/llm/generator.py`).
- **Figures:** when a problem needs a diagram, follow `docs/problem-images.md`
  (when to add one, SVG how-to, and the `content/problems/<slug>/assets/` +
  `/problems/{slug}/assets/{filename}` serving API). Bulk text imports go through
  the `/bulk-import` skill, which also fixes plain-text formatting damage.
- Keep this file and `docs/` in sync with reality as the app grows.
