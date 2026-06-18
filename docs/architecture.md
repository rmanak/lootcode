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
                │  • startup: create tables + seed content     │
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
                             │ harness.py     │  runs the solver function
                             │ per test, with │  against each test under
                             │ rlimits/timeout│  CPU/mem/PID/time limits
                             └────────────────┘
```

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
