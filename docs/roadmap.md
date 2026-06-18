# Roadmap

> What's done and what's next. The lootcode V1 loop (browse → solve → run →
> score) is working. Reorder the rest to taste; check items off as they land.

## Phase 0 — Foundations ✅
- [x] Repo scaffold, docs, content spec, Claude Code config.
- [x] PRD filled in; stack chosen (FastAPI + SQLite + Jinja2/CodeMirror).
- [x] FastAPI app, SQLAlchemy models, content loader + `scripts/seed.py`.

## Phase 1 — Walking skeleton ✅
- [x] List + filter problems by difficulty, topic, and title search.
- [x] Problem page with CodeMirror Python editor + starter code.
- [x] Run against all tests end-to-end with per-visible-test feedback.
- [x] Sandboxed `subprocess` executor (rlimits + timeouts) + adversarial tests.

## Phase 2 — Solve & score ✅ core / 🚧 polish
- [x] Weighted scoring; hidden tests counted but never revealed.
- [x] Cookie identity; solved list + submission history (`/me`).
- [x] Admin: add a problem by hand; generate + auto-verify problems via Claude API.
- [ ] Richer results UX (expected-vs-actual diff for visible failures).
- [ ] Pagination / sorting on the problem list as the bank grows.

## Phase 3 — Content & hardening
- [ ] Grow the problem bank (AI-assisted) across topics and difficulties.
- [ ] Default to the `docker` executor; build/publish `lootcode-runner` in CI.
- [ ] Rate limiting; basic metrics and structured logging.
- [x] **Optional accounts + guest claim/merge** — opt-in username/password login
  so progress is portable across browsers/devices; guests stay the no-login
  default, and a guest who logs in keeps their anonymous progress (merged into
  the account). Implemented: `docs/user-accounts-v2.md`. *(Follow-ups: sign the
  `lc_uid` cookie / move to a session id; gate admin with `is_admin`.)*
- [ ] Real (3rd-party / SSO) auth if you expose lootcode beyond a trusted LAN.

## Phase 4 — Polish & growth
- [ ] Streaks / progress dashboard; per-topic mastery.
- [ ] Efficiency tests (time/memory affecting score).
- [ ] More solver languages (add a per-language harness + runner image).

## Later / Someday
- Contests, classrooms / autograding, editorials & hints, recommendations.
