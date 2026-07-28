# On-the-fly AI help ("Get More Help with AI")

A solver who has read all of a problem's stored hints and is *still* stuck can ask
for one extra, more-concrete hint generated live. It appears on the problem page
below the last stored hint, behind a **✨ Get More Help with AI** button that
mirrors the admin "Generate with AI" look.

This is the interactive cousin of the bulk hint pipeline (see
[hint-generation.md](hint-generation.md)). The bulk pipeline pre-authors up to 3
progressive, gated hints and stores them; this feature generates a *fourth*,
deliberately-more-revealing hint on demand and does **not** store it.

## How it works

1. **Startup probe.** On boot (`app/main.py` lifespan) the server does a cheap
   `GET /v1/models` against the configured endpoint
   (`app/llm/help_generator.probe_endpoint`). The result is cached in
   `settings.llm_help_available`. Any failure — server down, `openai` not
   installed, auth rejected, timeout — just leaves the feature off.
2. **The button.** `problem.html` renders the button enabled when
   `ai_help_enabled` is true, otherwise greyed out (`.btn.disabled`) with a small
   note telling you which env var to set. This matches the admin page's pattern.
3. **Generation.** Clicking it POSTs to `/api/problems/{slug}/help`
   (`app/routers/submissions.py`). The route snapshots the problem **title +
   statement + existing hints**, then streams the model's output back as
   Server-Sent Events (`{"type": "delta"|"error"|"done"}`).
   `app/llm/help_generator.stream_help` talks to the endpoint with the official
   `openai` client (`stream=True`), reasoning/thinking off for speed.
4. **The UI** (`app/static/app.js`) reads the SSE stream, renders the hint token by
   token in an accent-coloured card under the button, and shows a progress bar +
   elapsed timer while it streams.

## The prompt

Lives in `app/llm/help_prompt.txt` (literal-token templating, like the other
prompts). It receives the title, statement and existing hints, and asks for **one**
3–5 sentence hint that (a) does not repeat any existing hint, (b) takes a concrete
step further, (c) still leaves the final "aha" to the solver. It is allowed to be
more revealing than the stored hints — the user is stuck by the time they click.

## Configuration

All optional; sensible defaults point at a local llama.cpp `llama-server`.

| Env var | Default | Purpose |
|---------|---------|---------|
| `LLM_HELP_URL` | `LLM_SERVER_URL` or `http://localhost:8080` | Base URL of the OpenAI-compatible endpoint (`/v1` appended if missing). |
| `LLM_HELP_API_KEY` | `LLM_API_KEY` or `sk-no-key-required` | Bearer token. llama.cpp ignores it; set it for cloud providers. |
| `LLM_HELP_MODEL` | `LLM_MODEL` or `local-model` | Model id sent in the request (llama.cpp largely ignores it). |

Because the defaults fall back to the same `LLM_SERVER_URL` / `LLM_API_KEY` /
`LLM_MODEL` the bulk hint generator uses, an existing local Qwen setup enables this
feature with no extra configuration.

### Re-checking the connection without a restart

The probe runs **once at startup**, so a lootcode started before the LLM server
would otherwise stay off for its whole lifetime. The off-state notice on **`/admin`**
(under the greyed-out "Generate with AI") carries a small **↻ Re-check connection**
button — the one place to re-probe. It posts to `POST /api/llm/refresh`, which
re-runs the same probe (`help_generator.refresh_availability`, also used by the
startup lifespan), updates `settings.llm_help_available`, and returns
`{available, endpoint, ai_help_enabled, generation_enabled}`. On success the page
reloads and **both** AI features come up enabled — the flag is global, so the problem
page's button works on its next load too (its own off-state note just points at
`/admin`; deliberately no button there, to keep the solver page uncluttered). Front
end: `app/static/llm_refresh.js` (any element with `data-llm-refresh`).
