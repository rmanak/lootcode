# Security & threat model

> Living document. The dominant risk is **executing untrusted code** — see
> `docs/code-execution.md`. This file covers the broader picture.

## Assets to protect

- Users' accounts and private submission code.
- Hidden test cases (leaking them undermines scoring).
- Platform secrets (DB creds, auth secret, OAuth secrets).
- Availability (don't let one user's run starve others).

## Primary threats & mitigations

| Threat | Mitigation |
|--------|------------|
| Malicious code escaping the sandbox | Strict isolation; see `code-execution.md`. |
| Resource exhaustion / DoS via runs | Per-run CPU/mem/time/PID/output caps; per-user rate limits; queue backpressure. |
| Leaking hidden tests | Hidden tests never sent to the browser; only pass/fail surfaced for them. |
| Stealing secrets from runs | No secrets in the sandbox env; network disabled. |
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

Any change to `services/executor/` or a code-running path requires a security
review (use the `executor-security-reviewer` subagent) before merge.
