# Tech stack

> **Status: resolved & implemented.** Chosen to be lightweight and easy to run
> on a home/LAN server (Python backend, no Node build step, single-file DB).

## What we use

| Layer | Choice | Why |
|-------|--------|-----|
| Language | Python 3 | Required; also the only solver language in V1. |
| Web framework | **FastAPI** | Modern, async, typed, minimal. Serves UI *and* API. |
| Frontend | **Jinja2 templates + CodeMirror** (CDN) | No Node/build step — one process, `pip install`, run. Syntax-highlighted editor. |
| Database | **SQLite + SQLAlchemy** | Zero-config single file; perfect for a home server. |
| Server | **uvicorn** | ASGI server; `HOST=0.0.0.0` to expose on the LAN. |
| Code execution | in-process **subprocess** sandbox (default) or **docker** | "Simple that works"; Docker is the Judge0-style hardened option. See `docs/code-execution.md`. |
| Identity | cookie-based, no passwords | "Nothing fancy"; per-person progress on a LAN. |
| AI generation | **Anthropic Claude API** (`claude-opus-4-8`) | Authoring help; optional, off unless `ANTHROPIC_API_KEY` is set. |
| Tests | **pytest** | Incl. adversarial executor tests. |

## Decisions (resolved)

1. **Backend framework** → FastAPI (best modern Python option; lighter than Django,
   more batteries than Flask).
2. **Backend language** → Python 3.
3. **Build vs. buy the executor** → built a small two-backend executor. `subprocess`
   for zero-dependency local use; `docker` (`--network=none`, dropped caps, capped
   memory/CPU/PIDs) for real isolation. Judge0 remains a drop-in alternative if you'd
   rather run it.
4. **Auth** → cookie identity, no passwords. Put the app behind auth/VPN if you expose
   it beyond a trusted network.
5. **Hosting** → run directly with uvicorn, or `docker compose up`. SQLite means no
   separate DB server.

## If you outgrow these

- **More languages:** add a per-language harness + runner image (the executor and
  problem schema already allow multiple `languages`).
- **More users / heavier load:** move to Postgres (swap `DATABASE_URL`), add a queue
  (Redis + a worker) so runs are async, and default the executor to `docker`.
- **Frontend interactivity:** the server-rendered UI can be progressively enhanced or
  replaced with an SPA hitting the same JSON API.
