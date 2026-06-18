# User accounts V2 — optional login + guest claim/merge

> **Status: IMPLEMENTED (2026-06-17).** Optional username/password accounts with
> lossless guest claim + login-merge; guests remain the no-login default. Identity
> is now **portable and recoverable** across browsers/devices. Deferred (by owner):
> admin gating (`is_admin`) and cookie signing — see scope notes below.
> See also `docs/roadmap.md`, `docs/data-model.md`, `docs/security.md`.

## Implementation progress (resumable — update as you go)

Resumability anchor is **this checklist + files on disk** (the repo currently has
no git history and the owner hasn't asked to commit). To resume: read this
checklist, run `python -m pytest -q`, then continue at the first unchecked box.

- [x] **S1 — Schema.** Add nullable `username`/`email`/`password_hash`/`claimed_at`/
  `last_login_at` to `User` (`app/models.py`); extend `app/db.py:_migrate()` with
  the `users` ALTERs + unique indexes on username/email. *(done; migration verified
  against existing DB.)*
- [x] **S2 — Auth helpers.** `app/auth.py`: stdlib-`scrypt` `hash_password`/
  `verify_password`, username/email normalization + validation. *(done; smoke-tested.)*
- [x] **S3 — Store ops.** `create_account`, `authenticate`, `merge_user` in
  `app/store.py` (uniqueness checks, lossless claim, guest→account merge).
  *(done; smoke-tested all paths incl. case-insensitive dup + merge.)*
- [x] **S4 — Middleware.** Stash `is_account`/`username` on `request.state`
  (`app/main.py`); keep guest-minting unchanged. *(done.)*
- [x] **S5 — Routes.** `GET/POST /account` (create+claim), `POST /login` (+merge),
  `POST /logout` in `app/routers/pages.py`; set/clear `lc_uid` cookie. *(done.)*
- [x] **S6 — Templates.** `account.html`; header account state in `base.html`;
  identity line on `progress.html` (`/me`); styles in `app.css`. *(done; E2E
  smoke-tested via TestClient.)*
- [x] **S7 — Tests.** `tests/test_accounts.py`: lossless claim, login-merges-guest,
  duplicate username/email refused, short/bad password refused, logout→fresh guest.
  *(7 tests; full suite 35 passed.)*
- [x] **S8 — Docs.** Status → IMPLEMENTED; `docs/data-model.md` User table updated;
  bearer-cookie tradeoff noted in `docs/security.md`; roadmap box checked.

**Scope notes for this build (per owner, 2026-06-17):**
- Admin stays **ungated** for now — `is_admin` column deferred (not in this work).
- Keep the **raw user-id `lc_uid` cookie** (V1 bearer scheme) so existing guests
  keep their progress; signing/session-id is a documented follow-up, not now.
- Password hashing uses **stdlib `hashlib.scrypt`** (no native dependency to build
  on the home server); `passlib`/argon2 remains a valid future swap.

## Goal & non-goals

**Goal.** A guest can *optionally* create an account (or log in to an existing
one) so their progress follows them across browsers, devices, and incognito —
and a guest who logs in doesn't lose the practice they did while anonymous.

**Non-goals / firm constraints.**
- **Guest stays the default.** No login wall, ever. A first-time visitor is still
  a cookie-minted guest with full read/solve/score access. Accounts are opt-in.
- No third-party identity provider in this phase (OAuth/SSO is "Later").
- Not a multi-tenant/teams system — single shared bank, per-user progress only.

## Where we are today (V1)

Identity = one cookie. The HTTP middleware in `app/main.py:33` reads `lc_uid`;
if missing/unknown it creates a `User(name="guest")` and sets the cookie
(`httponly`, `samesite=lax`, ~2-year max-age). That UUID **is** the identity:
all `Submission` rows are keyed by `user_id` (`app/models.py:94`), the solved set
is derived from them (`store.user_solved_problem_ids`), and the display name is a
free-text column changed via `pages.set_name` (`app/routers/pages.py:288`).

Consequences this plan fixes: clearing cookies, switching browser/device, or
opening incognito all mint a *new* user — progress looks "lost" (it's actually
stranded on the old cookie), with no recovery path.

## Core idea: a User row is a guest until it's "claimed"

Keep one `User` table for both guests and account-holders. A row is a **guest**
while it has no credentials; setting credentials **claims** it. This means the
common "create account" path needs **no data migration at all** — the
submissions are already on that row.

### Schema changes (`app/models.py`)

Add nullable auth columns to `User` (all `NULL` ⇒ pure guest, unchanged V1
behavior):

| field | type | notes |
|-------|------|-------|
| `username` | string, unique, nullable | login handle; `NULL` for guests |
| `email` | string, unique, nullable | optional; enables future reset/magic-link |
| `password_hash` | string, nullable | `NULL` ⇒ unclaimed guest. Use `argon2`/`bcrypt` (add `passlib[argon2]`) |
| `claimed_at` | timestamp, nullable | when the row became an account |
| `last_login_at` | timestamp, nullable | |
| `is_admin` | bool, default `False` | gate `/admin` (today it's effectively open — see security note) |

`name` stays as the display name. On claim, default `name` to `username` if it's
still `"guest"`. Migration: the table is small and auto-created; add columns with
a tiny one-off migration (or a guarded `ALTER TABLE` at startup), since we don't
run Alembic yet.

## The three flows

### 1. Create account (in-place upgrade — the frictionless win)
Current guest fills username + password (email optional). We set
`username/password_hash/claimed_at` **on their current row** and keep the same
`lc_uid` cookie. **No merge needed** — their guest progress is already theirs.
This is the answer to "I don't want to lose progress": claiming is lossless by
construction.

### 2. Log in (and merge — flow #4)
A visitor is *always* a guest row first (the middleware ran). When they log in to
a **different existing account**:
1. Verify `username` + `password_hash`.
2. **Merge** the current guest row into the target account (below).
3. Repoint `lc_uid` to the target account's id; continue as that account.

This is what makes incognito / a new laptop "just work": log in and your real
history is back, plus anything you solved as a guest in this session.

### 3. Log out
Clear the session/cookie and mint a fresh guest on the next request (back to V1
default). Logging out never deletes the account row.

## Merge-on-claim semantics (flow #4 detail)

When merging guest `G` into account `A`:
- **Reassign** `G`'s `Submission` rows to `A` (`UPDATE submissions SET user_id=A
  WHERE user_id=G`). The solved set is derived from submissions, so it unions
  automatically — no separate solved table to dedupe.
- A problem solved by both stays solved (idempotent); keep all submission history
  from both for an honest `/me` timeline. Optional: tag merged rows for audit.
- **Delete** (or tombstone) the now-empty guest row `G` so we don't accumulate
  orphans.
- Do it in **one transaction**; if it fails, leave the guest cookie intact.
- Edge cases: don't merge a *claimed* row into another (refuse — that's "switch
  account", just repoint the cookie, no reassignment); a guest with zero
  submissions is a no-op merge (just repoint + delete).

## Sessions & cookie hardening

V1 puts the raw user id in `lc_uid`, so the cookie is a bearer token — fine for
anonymous guests, weak once a password is involved. Minimum bar for V2:
- **Sign the cookie** (e.g. `itsdangerous`) so ids can't be forged/enumerated, or
  move to a server-side/`JWT` session id distinct from the user id (lets us log
  out and rotate without touching `user_id`).
- Set `Secure` when served over TLS; keep `httponly` + `samesite=lax`.
- Hash passwords with argon2/bcrypt; never log credentials; add basic
  rate-limiting on the login route (ties into the Phase 3 rate-limit work).

## UI surface (minimal)

- A small account menu in the header: when guest → "Create account / Log in";
  when claimed → username + "Log out". Reuse the existing name-edit affordance
  area near `app/routers/pages.py:281-291`.
- Two tiny forms (create, login) — server-rendered, no SPA. Inline errors for
  taken username / bad credentials.
- `/me` gains a one-line identity state ("Guest — create an account to save
  progress across devices" vs "Signed in as <username>").

## Implementation sketch (suggested order)

1. Schema: add nullable auth columns + `is_admin`; tiny startup migration.
2. Auth helpers: `passlib` hashing; `store` functions `create_account`,
   `authenticate`, `merge_user(into, from)`.
3. Routes in `pages.py`: `POST /account` (create/claim), `POST /login`,
   `POST /logout`; wire merge into login.
4. Middleware (`app/main.py:33`): keep guest-minting; switch `lc_uid` to a
   signed value; on login set it to the account id.
5. Gate `/admin` on `is_admin`.
6. Tests: claim-is-lossless, login-merges-guest-submissions, double-account
   refusal, logout→fresh-guest, signed-cookie tamper rejected.
7. Docs: update `docs/data-model.md` (User table) and `docs/security.md`.

## Acceptance criteria

- A brand-new visitor still solves problems with **no login** (V1 parity).
- A guest who creates an account keeps every prior submission (no migration).
- Logging in from incognito/another browser shows the account's full history
  **plus** anything solved as a guest in that session; the guest row is gone.
- Logging out returns to a fresh guest; the account is untouched.
- Tampering with the identity cookie does not grant another user's account.
