# Architecture

A single **FastAPI** application serves both the server-rendered UI and a small
JSON API. Code execution happens **in-process, synchronously** (fast enough for a
home instance; p95 target ≤ 10s). No separate frontend, queue, or DB server.

## Components

```
                ┌──────────────────────────────────────────────┐
                │  Browser                                     │
                │  Jinja2 pages + CodeMirror editor + app.js   │
                └───────────────┬──────────────────────────────┘
                                │ HTML  +  POST /api/.../run (JSON)
                ┌───────────────▼──────────────────────────────┐
                │  FastAPI app (app/main.py)                   │
                │  • identity middleware (cookie → User)       │
                │  • routers: pages / submissions / admin      │
                │  • startup: create tables + seed content,    │
                │    then load optional extensions (icf/)      │
                └───┬───────────────┬──────────────────┬───────┘
                    │               │                  │
            ┌───────▼──────┐ ┌──────▼─────────┐ ┌──────▼───────────┐
            │ SQLite (ORM) │ │ app/executor   │ │ app/llm          │
            │ problems,    │ │ run user code  │ │ Claude API:      │
            │ submissions, │ │ in a sandbox   │ │ generate+verify  │
            │ users        │ │ (UNTRUSTED)    │ │ problems (admin) │
            └──────────────┘ └──────┬─────────┘ └──────────────────┘
                                    │ subprocess (default) or docker
                             ┌──────▼─────────┐
                             │ sandbox.py     │  the shared launcher:
                             │  → harness.py  │  rlimits, own process group,
                             │                │  throwaway dir, backend choice
                             └────────────────┘
                   (the optional icf/ extension puts its own harness
                    behind the same launcher — see docs/extensions.md)
```

## Optional extensions

A feature can live in its own top-level folder and be deleted without a trace:
`app/extensions.py` imports each optional package by name at startup and lets
it `register(app)` — mounting routers, a static dir, its own templates, its own
database — and core reads back only a nav link and a set of identity roots.
Nothing in `app/` imports an extension, and the loader is a no-op when the
folder is absent.

`icf/` is the one that exists: the Industry Coding Framework, four-level timed
assessments. It reuses the sandbox launcher and the CodeMirror bundle and keeps
everything else (its problems, its SQLite file, its templates) to itself. See
`docs/extensions.md` and `icf/README.md`.

## Run/score flow (the critical path)

1. User clicks **Run & Score**; `app.js` POSTs the code to
   `/api/problems/{slug}/run`.
2. `submissions.py` loads the problem + tests and calls `executor.run_submission`.
3. The executor writes the code + a payload (function name, params, per-test
   inputs — **not** the expected outputs) into a throwaway dir and runs
   `harness.py` in a sandbox. The harness calls the solver once per test and
   reports each return value, timing, and any error.
4. The router compares each returned value to the expected value (hidden
   expectations never enter the sandbox), computes a weighted score, and saves a
   `Submission` + per-test `TestResult` rows.
5. The browser renders pass/fail per visible test plus the aggregate score;
   hidden tests contribute to the score but only their pass/fail is revealed.

## Content vs. database

`content/problems/` is the durable, human-editable source. On startup (empty DB)
or via `scripts/seed.py` it's loaded into SQLite, which is the runtime source of
truth. Problems created via Admin are written back to `content/` too.

## Why synchronous (for now)

A home/LAN instance has few concurrent users, so running code inline keeps the
system to one process and one file — nothing to operate. The seam is
`executor.run_submission`; to scale, move that call behind a queue + workers and
switch the executor backend to `docker`. See `docs/tech-stack.md` → "If you
outgrow these".
