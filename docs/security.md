# Security & threat model

> Living document. The dominant risk is **executing untrusted code** — see
> `docs/code-execution.md`. This file covers the broader picture.

## The trust boundary is the network

Read this before deploying anything. lootcode is built for a **single user on a
home LAN**, and that is a deliberate decision, not an oversight — but it only
holds if you know exactly what it buys and what it costs.

**There is no authentication anywhere.** Specifically:

- **`/admin/*` is open to anyone who can reach the port.** Any visitor can
  create, edit or overwrite problems in the bank — statements, tests, canonical
  solutions — through `POST /admin/new` and `POST /admin/problems/{slug}/edit`.
  Those writes go to the database *and* to `content/` on disk.
- **`POST /admin/verify` executes arbitrary submitted Python.** It exists so an
  author can check a draft before saving, and it takes the code straight from
  the request body. It runs in the same sandbox as a normal submission, which
  bounds CPU, memory and processes — and nothing else.
- **The default `subprocess` backend does not block network access**
  (`app/executor/subprocess_executor.py`). Submitted code can open sockets, and
  therefore can reach anything your server can reach: your LAN, your router's
  admin page, cloud metadata endpoints. Only the `docker` backend
  (`EXECUTOR_BACKEND=docker`) isolates the network.
- The `lc_uid` identity cookie is an unsigned bearer token (see the account-takeover
  row below).

So: **anyone who can open the port can run code on your machine and rewrite your
problem bank.** On a LAN you already trust, with a single user, that is a
reasonable trade for the simplicity it buys. Anywhere else it is not.

### The app refuses to bind to the network by accident

Because the boundary is the network, binding beyond loopback has to be a
decision. lootcode **refuses to start** on a non-loopback bind unless you set:

```bash
LOOTCODE_TRUST_LAN=1
```

This is checked in the lifespan (so it applies however you launch — `uvicorn
--host`, `UVICORN_HOST`, `python -m app.main`, docker), and it is not a security
control: it converts a silent exposure into a deliberate one. See
`app.main.check_bind_is_intentional`.

**Before exposing lootcode beyond a trusted LAN**, at minimum: put `/admin/*`
behind authentication, switch to `EXECUTOR_BACKEND=docker`, sign the identity
cookie, and serve over TLS.

## Assets to protect

- Users' accounts and private submission code.
- Hidden test cases (leaking them undermines scoring).
- Platform secrets (DB creds, auth secret, OAuth secrets).
- Availability (don't let one user's run starve others).

## Primary threats & mitigations

| Threat | Mitigation |
|--------|------------|
| Malicious code escaping the sandbox | Strict isolation; see `code-execution.md`. |
| Resource exhaustion / DoS via runs | Per-run CPU/mem/time/PID/output caps. Submitted code is capped at 256 KB and stored stdout at 4,000 chars per test (`app/routers/submissions.py`). Per-user rate limits and queue backpressure are **not** implemented. |
| Leaking hidden tests | Hidden tests never sent to the browser; only pass/fail surfaced for them. |
| Stealing secrets from runs | No secrets in the sandbox env. **Network is only disabled on the `docker` backend** — the default `subprocess` backend does not block it. |
| Rewriting the problem bank | **Not mitigated: `/admin/*` is unauthenticated.** Every save is written to the `lootcode.audit` log so there is at least a trail. See the trust boundary above. |
| Flipping the LLM feature flags | `POST /api/llm/refresh` is unauthenticated and sets the process-wide `settings.llm_help_available`, which gates the admin generation routes. Throttled to one real probe every 3 s; replayed otherwise. |
| Account takeover | Optional accounts hash passwords with stdlib scrypt. **Known V2 tradeoff:** the `lc_uid` cookie is the raw user id (a bearer token — `httponly`+`samesite=lax`, but unsigned), kept for V1 compatibility so existing guests don't lose progress. Acceptable on a trusted LAN; sign the cookie or move to a session id before any wider exposure. CSRF protection + `Secure` over TLS still to do. See `docs/user-accounts-v2.md`. |
| Injection (SQL/template) | Parameterized queries (ORM), input validation at API edge. |
| Scraping/abuse | Rate limiting, auth required for submit, bot mitigation. |
| Supply chain | Pin deps, lockfiles, Dependabot/audit in CI. |

## Data handling

- User code is private to the user; never expose it via public endpoints.
- Cap and sanitize captured stdout/stderr before storing/showing.
- Log metadata, never secrets or full user code in app logs.

## Secrets

- Local: `.env` (gitignored). Prod: a real secrets manager.
- The executor sandbox gets **no** platform secrets in its environment.

## Review gate

Any change to `app/executor/` or a code-running path requires a security
review (use the `executor-security-reviewer` subagent) before merge.
