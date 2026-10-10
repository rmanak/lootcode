# On-the-fly AI help ("Get More Help with AI")

A solver who has read all of a problem's stored hints and is *still* stuck can ask
for one extra, more-concrete hint generated live. It appears on the problem page
below the last stored hint, behind a **✨ Get More Help with AI** button that
mirrors the admin "Generate with AI" look.

The same endpoint (and availability flag) also backs the problem page's
**✨ Analysis** button — an AI review of the solver's code; see
[ai-analysis.md](ai-analysis.md).

This is the interactive cousin of the bulk hint pipeline (see
[hint-generation.md](hint-generation.md)). The bulk pipeline pre-authors up to 3
progressive, gated hints and stores them; this feature generates a *fourth*,
deliberately-more-revealing hint on demand and does **not** store it.

## How it works

1. **Availability probe.** On boot (`app/main.py` lifespan) the server does a cheap
   `GET /v1/models` against the configured endpoint
   (`app/llm/help_generator.probe_endpoint`), then keeps re-running it in the
   background every `LLM_HELP_PROBE_INTERVAL` seconds (`watch_availability`). The
   result is cached in `settings.llm_help_available`. Any failure — server down,
   `openai` not installed, auth rejected, timeout — just leaves the feature off.
2. **The button.** `problem.html` renders the button enabled when
   `ai_help_enabled` is true, otherwise greyed out (`.btn.disabled`); hovering it
   then explains why and which env var to set (the **✨ Analysis** button shows the
   same text). `app/static/llm_status.js` then polls
   `GET /api/llm/status` and flips the button (and the **✨ Analysis** button) on
   or off in place as the endpoint comes and goes — no reload.
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
| `LLM_HELP_PROBE_INTERVAL` | `10` | Seconds between background re-probes of the endpoint. `0` turns the watcher off (startup probe + manual re-check only). |

Because the defaults fall back to the same `LLM_SERVER_URL` / `LLM_API_KEY` /
`LLM_MODEL` the bulk hint generator uses, an existing local Qwen setup enables this
feature with no extra configuration.

### Following the LLM server up and down

Start lootcode before the LLM server, or stop the LLM server while lootcode runs,
and the AI features follow on their own:

- **Server side.** The lifespan starts `help_generator.watch_availability`, an
  asyncio task that calls `refresh_availability` (the same probe, in a worker
  thread) every `LLM_HELP_PROBE_INTERVAL` seconds and logs only transitions
  (`LLM endpoint … became available`). The flag gates the routes, so
  `/help`, `/analyze` and admin generation answer 503 again once it drops.
  Outbound traffic is one `GET /v1/models` per interval, however many tabs are open.
- **Problem page.** `app/static/llm_status.js` polls `GET /api/llm/status` every
  5 s while the tab is visible (and once on becoming visible). That route only
  reads the cached flag — no outbound request — and returns
  `{available, ai_help_enabled, generation_enabled}`. On a change the script fires a
  `lootcode:llm-status` event; `app.js` (this button + its hover text) and
  `analysis.js` listen and toggle in place. A hint or analysis already streaming is
  left to finish, and the new state applies when it does.

Worst case from "LLM up" to "button on" is one probe interval plus one poll (~15 s
with the defaults).

The off-state notice on **`/admin`** (under the greyed-out "Generate with AI") also
carries a **↻ Re-check connection** button for an immediate re-probe — and the only
one if the watcher is off (`LLM_HELP_PROBE_INTERVAL=0`). It posts to
`POST /api/llm/refresh`, which runs the same probe, updates the flag, returns
`{available, endpoint, ai_help_enabled, generation_enabled}` and reloads the page on
success. Front end: `app/static/llm_refresh.js` (any element with `data-llm-refresh`).
