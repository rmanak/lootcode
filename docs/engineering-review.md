# lootcode — Engineering Review
> **Stale section warning (2026-07-29):** everything below about `testgen/`,
> `strengthen_tests.py`, `oracle.py`, `strengthen_scheduler.py`,
> `collect_candidates.py`, `export_strengthened.py` and the `test-strengthener`
> agent is obsolete — that subsystem was **deleted**. See `docs/test-strengthening.md`.


> **Status: reference.** Findings audit conducted 2026-07-28 against HEAD `8215128`
> (working tree: 12 modified files, 1 untracked). The remediation plan derived from
> this document is [`engineering-plan.md`](engineering-plan.md).

## Scope & method

A full read of `app/` (35 files, 8,346 LOC), `scripts/` (24 files, 24,828 LOC),
`tests/` (8 files, 1,352 LOC), `docs/` + `specs/` (26 markdown files), and `.claude/`
(8 agents, 4 skills, 2 commands). Content trees were counted but not read
(`content/problems/` = 738 problems, `content/problems-extended/` = 435, DB = 1,173).

Findings marked **[V]** were reproduced by hand during the audit — the file was read
or a command was run to confirm the claim. Everything else comes from a systematic
sweep and carries a file:line citation you can check directly. No claim in this
document is inferred from naming alone.

Nothing was modified. No test suite was executed (see §C.1 for why that is itself a
finding).

---

## Part A — Correctness & reliability

### A.1 Extended-root problems serve no figures **[V]**

`app/routers/pages.py:391` resolves a problem's `assets/` dir under
`settings.CONTENT_DIR` only:

```python
assets_dir = (settings.CONTENT_DIR / slug / "assets").resolve()
```

But `app/config.py:87-90` defines `content_dirs` as **both** roots, and
`store.seed_from_content` seeds both. **114 of the 435 extended problems have an
`assets/` directory** (verified: `ls -d content/problems-extended/*/assets | wc -l`
→ 114; the default root has 32). Every figure in those 114 problems 404s.

The rest of the handler is genuinely careful — extension allowlist, traversal-token
rejection, `commonpath` containment check (`:384-396`). Only the root is wrong.

This is also a documentation trap: `docs/importing-problems.md:116-120` and
`docs/design-problems.md:94-98` both describe an import flow that copies figures into
`content/problems-extended/<slug>/assets/` and rewrites refs to
`/problems/<slug>/assets/<file>`. That flow runs correctly and produces files the
server will never serve. `docs/problem-images.md:72` happens to describe the
CONTENT_DIR-only behaviour accurately, so the docs contradict each other.

### A.2 Editing an extended problem writes a duplicate into the default root **[V]**

`app/routers/admin.py:59-66`:

```python
def _save(db: Session, data: dict) -> Problem:
    prob = store.upsert_problem(db, data)
    try:
        content.write_problem_files(data)
    except OSError:
        pass  # DB is the source of truth at runtime; file mirror is best-effort
    return prob
```

`content.write_problem_files` takes an optional root (`app/content.py:147`:
`def write_problem_files(data, content_dir: Path | None = None)`) and defaults to
`settings.CONTENT_DIR` (`:150`). `_save` never passes one. So editing any of the 435
extended problems writes a **second copy** into `content/problems/` — which is
tracked by git, unlike the extended root — and that copy then shadows or duplicates
the original on the next seed.

### A.3 The same three lines silently desync the DB from disk

The `except OSError: pass` above is the most consequential silent failure in the app.
`CLAUDE.md:88-89` states the invariant: *"The DB is the runtime source of truth;
`content/problems/` is the durable, human-editable mirror."* A full disk, a
permissions problem, or a read-only mount breaks that invariant with **no log line
and no user feedback**. The admin sees a success redirect. The next
`seed_from_content` does not have the problem.

### A.4 The identity middleware blocks the event loop on every request **[V]**

`app/main.py:48-77`. `attach_user` is `async def` and performs synchronous
SQLAlchemy/SQLite I/O directly on the event loop:

```python
async def attach_user(request: Request, call_next):
    ...
    with SessionLocal() as db:          # :58  sync I/O
        user = db.get(User, uid) if uid else None   # :59
        if user is None:
            user = User(name="guest")
            db.add(user); db.commit(); db.refresh(user)   # :62-64  sync write
```

Only two `async def` exist in all of `app/` (this and the lifespan); every route
handler is `def`, which FastAPI correctly offloads to a threadpool. This middleware
is therefore the codebase's **only** true blocking-async violation — and it runs on
every non-static request, including the SSE streams from
`/api/problems/{slug}/help` and `/admin/generate/*/stream`, which is precisely when
loop responsiveness matters.

Secondary problem in the same block: a `User` row is **created** for any request
without a valid `lc_uid` cookie. That includes every crawler, every 404, every
`/robots.txt` probe. There is no bot filter and no cleanup of unclaimed guests.

### A.5 SQLite is unconfigured for concurrent access **[V]**

`app/db.py:11-15`:

```python
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
```

No `PRAGMA journal_mode=WAL`, no `busy_timeout`, no `foreign_keys=ON`, no explicit
pool sizing. Default SQLite is rollback-journal with a **0 ms** busy timeout: one
writer blocks all readers, and a second concurrent writer gets an immediate
`database is locked`. Combine that with A.4 (every request writes) and FastAPI's
default 40-thread pool for sync routes, and this is the highest-probability
production failure in the repo.

`_migrate()` (`:40-115`) is a hand-rolled additive-DDL migration path with no
versioning — workable at this size, but worth naming as a known limit rather than a
surprise.

### A.6 A DB session is held open across the entire sandbox run

`app/routers/submissions.py:34` takes `db: Session = Depends(get_db)`, calls
`run_submission` at `:46`, and only writes at `:48-72`. The session — and its pooled
connection — is checked out for the full subprocess lifetime, which
`app/executor/subprocess_executor.py:73` bounds at
`import_budget_s + per_test_s * n_tests + 5.0` (default `EXEC_TIME_LIMIT_MS` is
10,000; `app/config.py:44`). Same pattern in `admin.new_submit` (`admin.py:400`) and
`edit_submit` (`:256`), where `validate_problem` runs the canonical in the sandbox
(`app/problem_validation.py:199`) while holding a session.

### A.7 Unbounded request inputs

- `RunBody.code` (`app/routers/submissions.py:21-22`) has no length bound and is
  stored verbatim in `Submission.code` (`app/models.py:196`, `Text`).
- `stdout` is truncated to 4,000 chars **on the way out** (`submissions.py:71`) but
  stored uncapped (`:60`).
- `admin.duplicate_check_api` (`:630`) and `admin.statement_stream` (`:533`) accept
  unbounded form text and forward it to an LLM call; the only cap is a `[:6000]`
  slice applied *inside* `generator.suggest_title_slug` (`app/llm/generator.py:538`).
- No rate limiting anywhere. Each `POST /api/problems/{slug}/run` spawns a subprocess
  allowed `EXEC_MEMORY_LIMIT_MB` (default 512 MB). There is no concurrency cap.
- `admin._sse_stream` (`:495-523`) spawns an unbounded number of daemon threads, one
  per generation request, each holding an LLM connection with a 300 s timeout
  (`generator.py:258`), with no cancellation — a disconnected client's thread runs to
  completion. The `queue.Queue()` at `:502` is unbounded.

### A.8 Logging is effectively absent **[V]**

`grep -c 'print(' app/**/*.py` → the only match is inside a docstring example
(`app/llm/hint_generator.py:25`). Good — no stray prints. But the replacement never
arrived: **`app/store.py:25` is the only `logging.getLogger` in 8,346 lines**, used
at exactly one site (`:113-114`), and there is no `basicConfig`/`dictConfig` anywhere
in `app/`, so even that one warning depends on uvicorn's root config.

Nothing logs sandbox failures, DB errors, LLM failures, the A.3 mirror failure,
guest-user creation, or admin writes. There is **no audit trail** for a problem bank
that unauthenticated routes can overwrite.

### A.9 Exception swallowing that hides real causes

There are **zero bare `except:`** in `app/`, and all 24 `except Exception` sites carry
`# noqa: BLE001` — so this is deliberate, not careless. These are the ones where the
swallow costs real diagnostic information:

| Location | What is lost |
|---|---|
| `app/routers/admin.py:63-65` | The disk-mirror failure (A.3) |
| `app/main.py:39-40` | *Why* the LLM probe failed (bad URL vs. missing `openai` vs. auth) — surfaces only as a permanently greyed-out button |
| `app/llm/help_generator.py:79-80`, `:93-94` | Same, for `POST /api/llm/refresh`; `llm_refresh.js:33` reports `No LLM at <endpoint>` regardless of cause |
| `app/routers/admin.py:593-594` | A failed `suggest_title_slug` degrades to "no similar problems found" — the **opposite** of the safe default for a duplicate gate |
| `app/llm/generator.py:648-650` | The final grade; the review page then shows an unverified draft indistinguishable from a verified one |
| `app/executor/subprocess_executor.py:107-111` | A corrupt `result.json` falls through to the generic "The run was stopped…" message (`:115-116`), misattributing a harness bug as a user timeout |
| `app/testgen/generators.py:1084` | A *raising* constraint validator is treated as "rejects", conflating a validator bug with a legitimate rejection |

### A.10 Config that has drifted into three sources of truth

`app/llm/hint_generator.py:41-49` and `app/testgen/candidates.py:28-30` read
`LLM_SERVER_URL` / `LLM_MODEL` / `LLM_API_KEY` from `os.environ` **directly at import
time**, bypassing `settings` — and with *different defaults* than
`app/config.py:59-64` uses for the same variables (`"local-model"` vs `"qwen36"`).
`hint_generator.py:109` reads `LLM_TIMEOUT`, which is not a `Settings` field at all.

Smaller duplications of the same kind: cookie max-age `63_072_000` hardcoded at
`main.py:75` and `pages.py:700` (the latter's comment acknowledges the duplication);
`MAX_HINTS = 3` at `content.py:15` and `hint_generator.py:52`; `COMPARE_MODES` at
`admin.py:38` and `problem_validation.py:68`; `_now()` at `models.py:52` and
`store.py:28`.

Worth a separate check: `app/config.py:51` defaults `ANTHROPIC_MODEL` to
`"claude-opus-4-8"`. If that id is stale, every Anthropic generation fails with an
API error that `generator.py:244` then swallows into a confusing fallback path.

### A.11 List-page cost scales with the bank **[V]**

`pages.index` (`app/routers/pages.py:400-572`) scans the full `problems` table
**three times per request**, hydrating complete ORM rows including `statement_md`,
`starter_code`, and `canonical_solution`: once at `:410`, again via `_topic_counts`
(`:481`→`:146`), again via `_unsolved_counts` (`:486`→`:132`). At 1,173 problems
that's ~3,500 fully-hydrated multi-KB rows — on every homepage hit, and on **every
keystroke**, since `list.js:53-56` refetches `/` after a 200 ms debounce. All
filtering after the SQL `WHERE` happens in Python (`:412-447`), and pagination slices
the already-materialised list (`:539`).

Related: `admin.dashboard` renders ~1,000 rows in one response
(`ADMIN_PROBLEMS_PER_PAGE = 1000`, `admin.py:56`); `pages.progress` (`:646-649`)
loads every submission a user has ever made and slices to 25 in Python;
`find_similar_problems` (`problem_validation.py:288-320`) recomputes stemmed tokens
and document frequencies for the entire bank on every call, and is called on every
AI-review render, every failed create, and every duplicate check.

---

## Part B — Security posture

**Owner decision (2026-07-28): single-user / LAN is the accepted trust boundary. No
authentication will be added.** This section records what that boundary actually
covers, so the decision is informed and documented rather than implicit.

### B.1 What is exposed

- **`/admin/*` has no authentication.** `app/routers/admin.py:1-5` acknowledges this
  in its docstring. `POST /admin/new` (`:398`) and
  `POST /admin/problems/{slug}/edit` (`:254`) write to the DB *and* to disk.
- **`POST /admin/verify` (`:384-388`) is unauthenticated arbitrary code execution.**
  It takes `VerifyBody.code` (`:316`) and passes it to `run_submission` (`:364`). It
  is sandboxed — rlimits, `start_new_session`, tempdir, kill-group — but
  `app/executor/subprocess_executor.py:8-10` explicitly documents that the default
  backend **does not block network access**. Anyone who can reach the app has an
  outbound-network-capable Python REPL, unmetered.
- **`POST /api/llm/refresh` (`app/routers/submissions.py:107`) is unauthenticated and
  mutates process-wide state** — it writes `settings.llm_help_available`
  (`config.py:73`), which `settings.generation_enabled` (`:79-84`) reads, which in
  turn gates the admin LLM routes (`admin.py:538`, `:558`, `:575`, `:653`, `:677`).
  So one unauthenticated endpoint controls whether another unauthenticated endpoint
  will make outbound LLM calls. It also triggers a network probe to `LLM_HELP_URL`
  on demand.
- Raw exception text reaches the browser at `submissions.py:164`, `admin.py:508`,
  `:563`, `:701`, `:703`, `generator.py:293`, `:627`, `help_generator.py:173` —
  including URLs, model names, and `scripts/` file paths.

### B.2 The gap between the decision and the code

The LAN-trust decision is sound *for a loopback or trusted-LAN bind*. The problem is
that nothing enforces or announces it: `settings.HOST` defaults to `127.0.0.1`
(`config.py:25`) but `Makefile:14` binds `10.8.0.1`, `docker-compose.yml` publishes
the port, and `README.md:45` tells users to bind `0.0.0.0`. There is no startup
warning and no doc stating the boundary. The remediation (a loud refusal to start on
a non-loopback bind without an explicit opt-in, plus a written trust model in
`docs/security.md`) is Phase 3 of the plan.

### B.3 What is genuinely well built

Worth recording so it isn't undone: the sandbox itself is careful (rlimits, process
group kill, tempdir, stdlib-only harness); `pages.problem_asset` (`:380-397`) does
path-traversal defence properly; `app/auth.py` uses stdlib `scrypt` correctly and is
the cleanest module in the tree; `app/models.py:180-183`'s `JSONText` TypeDecorator
is a subtle, correct fix for SQLite NUMERIC affinity corrupting big-integer answers,
and it has a dedicated regression test.

---

## Part C — The engineering floor

### C.1 Tests write to the live development database **[V]**

`TestClient(app)` runs the real lifespan (`app/main.py:21-40`), which calls
`init_db()` against `settings.DB_PATH` — defaulting to the repo-root `lootcode.db`,
**currently 21 MB and shared with the developer's running app**. No `LOOTCODE_DB`
override exists anywhere in `tests/`, the `Makefile`, or `.claude/`.

Consequences: `tests/test_accounts.py:17-25` inserts real `User` and `Submission`
rows (UUID-named, so they accumulate and nothing deletes them);
`tests/test_app.py:133-138` mutates the `Collection` table; `seed_collections` re-runs
on every `TestClient` construction. Tests are order- and history-dependent on a
mutable, gitignored artifact, so a CI-from-clean run and a local run are not the same
run.

`tests/test_jsontext_bigint.py:24-34` is the sole file that does this correctly
(a `tempfile.mkstemp` DB fixture). It is the model to follow.

This is why the audit did not execute the suite: running it would have been a state
change to the owner's live data.

### C.2 Coverage gaps

91 tests collected across 8 files. Modules with **zero** test reference — roughly
2,600 LOC:

| Module | LOC | Why it matters |
|---|---:|---|
| `app/problem_validation.py` | 479 | The pre-save gate every manual **and** AI admin write passes through (`CLAUDE.md:31`) |
| `app/llm/generator.py` | 674 | Generation orchestration |
| `app/llm/hint_generator.py` | 548 | generate / judge / verified loop |
| `app/tags.py` | 153 | `normalize_tags` runs on every content write |
| `app/testgen/{features,mutate,coverage,select,shrink}.py` | 851 | The coverage-first selection backbone |
| `app/executor/docker_executor.py` | 81 | The *hardened* backend — `grep -rn docker tests/` returns nothing |
| `app/llm/{help_generator,statement_store,draft_store}.py` | 309 | Incl. the new `refresh_availability` |

**22 of 33 routes have no test.** That includes 16 of 17 `/admin` routes — every
generation route, both verify routes, and `POST /admin/new`, which is the one
validated save path. The single `/admin` test is a bare
`assert client.get("/admin").status_code == 200` (`tests/test_app.py:44`).

No `conftest.py` exists; the `client` fixture is duplicated verbatim in three
modules. No coverage tool is installed, though `.gitignore:22-24` already reserves
`.coverage`, `htmlcov/`, `.ruff_cache/`, `.mypy_cache/` — aspirationally.

### C.3 No linter, formatter, type-checker, or CI — but the suppressions are written **[V]**

| Config | Present |
|---|---|
| `pyproject.toml`, `setup.cfg`, `ruff.toml`, `.flake8`, `mypy.ini`, `tox.ini`, `pytest.ini`, `.pre-commit-config.yaml` | **None** |
| `.editorconfig`, `Makefile`, `Dockerfile`, `docker-compose.yml`, `.dockerignore` | Yes |
| `requirements-dev.txt` | Yes — `pytest>=8.0` and `httpx>=0.27` only |
| `.github/workflows/` | One file, `claude.yml` — an `@claude` responder. **No job runs tests, lint, or types.** |

The striking part: **`app/` contains 37 `# noqa` directives using ruff-specific rule
codes** — `BLE001`×24, `N802`×5, `E402`×2, `A002`×2, `S307`, `S102`, `F401`, `ANN001`
(verified by `grep -rho 'noqa: [A-Z0-9]*' app/ | sort | uniq -c`). `S###` is
flake8-bandit, `ANN###` flake8-annotations, `A###` flake8-builtins — all ruff plugin
namespaces. The code is written *as if* ruff runs. Turning it on is nearly free
because the suppression work is already done.

Two consequences of having no `pytest.ini`: there is no `testpaths`, so a bare
`pytest` from the repo root **imports `scripts/test_llm_output.py`** at collection
(it emits a `PytestCollectionWarning` at `:146`). It collects nothing today; it will
break the day that file grows a `def test_*`.

### C.4 Dependencies are unpinned **[V]**

`requirements.txt` is 8 packages, every one a `>=` floor, with no lockfile and no
constraints file. A fresh `pip install -r requirements.txt` today can pull a FastAPI
or SQLAlchemy major that breaks the app, and nothing would catch it — there is no CI.

### C.5 Type-hint coverage is good in libraries, thin at the edges

Measured across 328 functions in `app/`: **242 return annotations (74%)**, parameter
annotations higher. The distribution is the interesting part — `auth.py`, `store.py`,
`tags.py`, `templating.py`, `config.py`, `db.py`, `content.py` and most of `testgen/`
are at 96–100%, while route handlers are the gap: `admin.py` 35%, `pages.py` 58%,
`submissions.py` 14%. Almost no `@router.get`/`@router.post` function has a return
annotation, and none declares a `response_model`, so FastAPI's generated OpenAPI
schema for the JSON API is untyped.

`app/executor/harness.py` (24% / 9%) is the other outlier and is defensible — it is
deliberately minimal stdlib-only sandbox code.

Style is otherwise consistent: ~88-char house limit, 68 lines exceed it, naming and
docstrings are genuinely good throughout (module docstrings explain *why*).

---

## Part D — Structure & duplication

### D.1 Business logic lives in HTTP handlers

`app/store.py` is a real service layer for user concerns and routers do use it — but
routers also talk to the ORM directly throughout (`pages.py:405-410`, `:417-418`,
`:600`, `:616`, `:623-628`, `:646-649`; `submissions.py:35`, `:48-61`;
`admin.py:210-216`, `:244`, `:266`, `:306`), and `main.py:24` and `:58-71` bypass
`store.py` entirely.

The bigger issue is domain logic with no HTTP dependency sitting inside route
modules:

- **`app/routers/pages.py`** — roughly **370 of 755 lines**. The whole progress model
  (`_unsolved_counts`:124, `_topic_counts`:138, `_topic_cloud`:153, `_first_solved`:201,
  `_blocks_by_local_date`:218, `_lay_out_week`:238, `_weekly_streak`:258,
  `_month_calendar`:294, `_parse_cal_month`:337, `_page_window`:352), plus the
  `PROVIDED_TYPE_DEFS` table (`:30-68`) — which duplicates the harness's class
  definitions **as strings** (`app/executor/harness.py:62-258`). `index` alone is 172
  lines.
- **`app/routers/admin.py`** — 758 lines, four unrelated responsibilities: form⟷data
  marshalling (~145 lines), CRUD routes (~200), an unsaved-problem verification
  service (~60), and the entire AI generation orchestration (~290, with near-zero
  coupling to the rest).
- **`app/llm/generator.py`** — 674 lines containing *two* generation architectures.
  `generate_problem` (`:408-457`) has **no caller in `app/`**; only the two-step flow
  is wired to the UI.

`app/routers/admin.py:34` imports a leading-underscore helper across routers
(`from .pages import _page_window`) — a signal that the shared pagination logic wants
its own module.

### D.2 Two inverted dependencies **[V]**

**`app/` imports from `scripts/` by mutating `sys.path` at import time**, in the
request path:

```
app/problem_validation.py:64-65   sys.path.insert(0, str(_SCRIPTS))
app/llm/generator.py:481-482      _sys.path.insert(0, str(scripts_dir))
```

`problem_validation.py:66` then does `import test_llm_output as _tlo`;
`generator.py:605` and `:640` pull `generate_problem_from_statement` and
`verify_json`. This is documented as deliberate, and the intent (don't re-implement
the validator) is right — but the result is that the web app depends at runtime on a
directory that is not a package, and `scripts/` is de facto a library that `app/` sits
downstream of.

**35% of the runtime package has no runtime importer.** Nothing in `app/` imports
`app.testgen` (2,393 LOC); its only consumers are `scripts/oracle.py`,
`strengthen_tests.py`, `collect_candidates.py`, `export_strengthened.py`, and
`tests/test_testgen.py`. Same for `app/llm/hint_generator.py` (548 LOC). Both are
offline authoring tooling living inside the served application package — they ship in
the Docker image and inflate the runtime dependency set.

### D.3 The duplication inventory

| What | Copies | Where |
|---|---:|---|
| OpenAI/Anthropic client construction (rstrip `/`, append `/v1`, build client) | **4**, with 4 different timeout policies | `help_generator.py:53-57`, `hint_generator.py:106-111`, `generator.py:253-259`, `testgen/candidates.py:102-108` |
| `_loads_loose` (fence-stripping JSON parse) | 2 | `generator.py:209-221`, `hint_generator.py:130-143` |
| The `response_format` degradation ladder (`json_schema` → `json_object` → `None`) | 3 | `hint_generator.py:240-269`, `:422-445`, `generator.py:271-293` |
| Hand-rolled "problem-like" shims | **4** | `admin.py:350-362`, `problem_validation.py:447-465`, `generator.py:166-183`, `:361-369` |
| The 14-key form⟷dict structure | **5** | `admin.py` `_form_view`:115, `_data_to_form`:155, `_blank_form`:145, `_raw_form`:183, `edit_submit`'s `typed`:272 |
| Executor payload construction | 2 | `subprocess_executor.py:58-69`, `docker_executor.py:35-47` |
| SSE frame encoding | 2 | `submissions.py:127-129` (`_sse`), `admin.py:519` (inlined) |
| **JS SSE reader loop — byte-identical** | **3** | `app.js:246-269`, `generate.js:48-75`, `generate_statement.js:119-146` (plus identical error preamble and progress-bar machinery) |
| Kind-toggle inline `<script>` — character-identical | 2 | `admin/new.html:153-169`, `admin/edit.html:79-95` |
| "Is this dir a problem?" test | 2 | `content.py:106`, `problem_validation.py:337-338` |

The problem-like shims deserve emphasis. `app/executor/__init__.py:74-114` already
defines `ProblemView` + `problem_view()`, and its docstring states the contract
explicitly: callers may pass an ORM row, a `load_problem_dir` dict, *"or any object
exposing these fields — and never a hand-picked subset."* Four hand-picked subsets
exist anyway, and one of them has already drifted: `generator.py:166-173`'s
`_ProblemLike` omits `kind`, `class_name`, and `class_methods`, so it silently cannot
grade class/design problems. That is exactly the failure `ProblemView` was written to
prevent.

### D.4 Frontend

12 templates (1,232 lines), 8 static files (1,497 lines) plus a committed 466 KB
minified `vendor/cm6.js` with no source map, version pin, or provenance note.

CSS is a single well-sectioned 751-line `app.css` with low duplication and no
preprocessor — fine at this size. All CSS is external (no `<style>` blocks anywhere),
which is good. Against that, **~122 lines of inline JS across 5 templates**
(`base.html:9-24`, `problem.html:175-195`, `progress.html:198-240`,
`admin/new.html:153-169`, `admin/edit.html:79-95`), and `_quick_picks.html` is the
only partial — the pagination `<nav>`, topic-chip loop, and problem-row `<tr>` are all
inlined rather than shared.

`list.js` is worth calling out as well-built: debounced search with a `seq` guard
against out-of-order responses (`:11`, `:39`) and region-swapping via `DOMParser`.

### D.5 The untracked file that will break the next commit **[V]**

`app/static/llm_refresh.js` is **untracked** (`?? app/static/llm_refresh.js`), while
`app/templates/admin/index.html:79` — a *tracked, modified* file — references it via
`{{ static('llm_refresh.js') }}`. A `git commit -a` ships the template without the
script.

It fails silently: `app/templating.py:40-41` catches the `OSError` from the missing
file and falls back to an unversioned URL rather than raising. The result is a 404 on
the script and an inert ↻ button, with nothing in the logs (there are no logs — A.8).

`docs/ai-help.md:67` already documents the file as shipped.

---

## Part E — `scripts/` and repo hygiene

### E.1 `scripts/` is 24.8k LOC with no shared library **[V]**

There is no `scripts/__init__.py` and no `scripts/_common.py`. `build_bank.py` alone
is 15,594 lines — 63% of all script code, and 13× the largest `app/` module.

Three mutually incompatible import conventions coexist: 18 scripts
`sys.path.insert(0, <repo root>)` then `import app.*`;
`export_strengthened.py:65` uses `from scripts.strengthen_tests import …`
(namespace-package style, requires cwd=root); `check_constraint_validators.py:41-42`
and `generate_class_validators.py:51` put **`scripts/` itself** on the path and
bare-`import` a sibling.

Re-implemented helpers:

- **`_iter_problem_dirs` — 4 copies**, and two are subtly weaker.
  `check_constraint_validators.py:64` and `improve_hints.py:76` are multi-root with a
  missing-root guard; `generate_hints.py:45` and
  `generate_constraint_validators.py:514` are **single-root with no guard**. All four
  duplicate what `app/content.py:111` `load_all_roots()` + `app/config.py:87`
  `content_dirs` already provide.
- **LLM reachability preflight — 3 copies** (`generate_hints.py:79-84`,
  `generate_constraint_validators.py:520-527`, plus the error string copy-pasted at
  `improve_hints.py:283-285`, `:415-416`, `:556-557`) — alongside the app's own
  `help_generator.probe_endpoint`.
- **`class Palette` (ANSI colours) — 2 verbatim copies** (`verify_bank.py:47-67`,
  `recheck_solutions.py:66-89`), with `improve_hints.py` open-coding `\033[` a third
  time.
- **18 scripts hand-roll argparse**, all repeating `--base-url` / `--model` /
  `--api-key` / `--slug` / `-j` / `--dry-run` / `-v` / `-q`. No shared parent parser.

The counterexample worth preserving: **nothing re-implements the sandbox.** 11 scripts
import `run_submission` from `app.executor`, and `verify_bank.py:11` states this as an
explicit invariant. That discipline held; the rest did not.

### E.2 `scripts/audit.py` audits the DB, not the disk

`scripts/audit.py:144-145` seeds only `if not db.query(Problem).count()`. On any
developer machine the DB is already populated, so **`audit.py` silently audits stale
content** unless you remember to re-seed first. Nothing in `CLAUDE.md:63-64` or
`README.md:64` warns you. `verify_bank.py` reads `content.load_all_roots()` directly
(`:236`) and does not have this bug.

This matters because `audit.py` is the *strictest* gate — it is the only thing
checking statement↔judge consistency and the "reversed valid answer is still
accepted" fairness property (`:109-135`).

### E.3 No single "check everything" entrypoint

The nearest thing is a five-line block a human copies out of `README.md:62-66`:
`pytest` → `seed.py` → `audit.py` → `verify_bank.py -j 8` →
`check_constraint_validators.py`. `Makefile` has `seed` but no `audit`, `verify`,
`lint`, `typecheck`, or `check` target. No CI job runs any of the four gates. No
pre-commit hook exists.

There *is* a cron job — but it's the wrong one: `.strengthen/new_crontab.txt` runs
`strengthen_scheduler.py` hourly, which *adds* test cases. Nothing periodically
verifies existing invariants.

### E.4 Dead code and untracked clutter

- **`scripts/find_duplicate_slugs.py`** (257 LOC) — **0 references** in `CLAUDE.md`,
  `README.md`, `docs/`, `specs/`, `.claude/`, `Makefile`, or any sibling script.
  Meanwhile `docs/duplicate-detection-plan.md:114-121` plans an `app/dedup.py` +
  `scripts/dedup.py` and never mentions this file.
- **`scripts/seed_one.py`** (50 LOC) — **0 references**; only self-references.
- `scripts/generate_hints.py` — superseded; `CLAUDE.md:176-178` already says to use
  `improve_hints.py` instead.
- Stale `.pyc` files in `scripts/__pycache__/` reveal four already-deleted scripts
  (`generate_input_validators`, `import_collection`, `import_design_problem`,
  `repair_flagged_cases`); the root `__pycache__/` holds six more from scratch modules
  (`buggy_sol`, `tmp_wrong_*`) run from the repo root.

Directories accumulating with no rotation: `staging/` (22 MB, 500 dirs),
`.hints/` (1.2 MB — `audit.html` alone is 622 KB, plus timestamped `.bak` files),
`constraint_validators/` (964 KB, 110 stale files superseded by the 738 in-tree
validators), `scratchpad/` (9 files from 2026-07-17 including three one-off `.py`
scripts that never made it into `scripts/`), and **~738 `__pycache__` dirs generated
inside `content/`** by `check_constraint_validators.py`, which make
`git status --ignored` unusable. A personal `resume.txt` sits in the repo root
(gitignored, so not leaked).

### E.5 Commit history **[V]**

40 commits. Roughly half carry no information: `stuff` (HEAD), `improve hint`,
`removed some duplicates`, `fixed verify json`, `removed files`, `fixed gitignore`,
`added class support`, `fixed admin page`, `claude`, `stuff`, `claude did this`,
`changed stuff`, `fixed something`, `fixed bug`, `improved tests`, `did stuff`,
`added stuff`, `blah blah`.

The good ones show the achievable standard — `Test-strengthening: coverage-first
selection (adversaries add-only)`, `Add TreeNode rich input/return type and migrate
tree problems`. Note the trajectory: the two PR merges (`#1`, `#3`) and their branch
commits are well-written; the direct-to-`master` commits are not.

`CONTRIBUTING.md:8-9` mandates Conventional Commits. **Zero of 40 commits use a
`feat:`/`fix:`/`docs:` prefix.** This is also the root cause of §F: with no readable
history and no changelog, nothing ever forces a documentation pass.

---

## Part F — Documentation drift

26 markdown files. **14 dead references, 22 factually-wrong claims.** Full remediation
list is in [`engineering-plan.md`](engineering-plan.md) §6; this section records the
findings.

### F.1 Dead references (doc names something that does not exist)

| Location | Reference | Reality |
|---|---|---|
| `docs/code-execution.md:3` | `services/executor` | `app/executor/` |
| `docs/security.md:39` | `services/executor/` | Same — and this is the **security-review gate** |
| `CONTRIBUTING.md:20` | `services/executor/` | Same |
| `.claude/agents/executor-security-reviewer.md:3` | `services/executor` | Same — and it is in the agent's `description:`, i.e. its selection trigger |
| `docs/code-execution.md:25,26,29` | `EXECUTOR_TIME_LIMIT_MS`, `EXECUTOR_MEMORY_LIMIT_MB`, `EXECUTOR_MAX_OUTPUT_KB` | `EXEC_*` (`app/config.py:44-46`) |
| `docs/code-execution.md:89` | `functionSpec` | `function_name` / `params` (`app/models.py:97-98`) |
| `docs/data-model.md:44` | `functionSpec`, `limits`, `scoring`, `isPublished` | All snake_case in reality |
| `docs/data-model.md:48-61` | Entities **`Language`** and **`Starter`** | Neither exists |
| `docs/api-design.md:11-63` | The entire `/api/v1/…` surface | **None of it exists.** Real: `POST /api/problems/{slug}/run\|known\|visit-later\|help`, `POST /api/llm/refresh` |
| `README.md:94` | `scripts/bank_new_p/` | Does not exist |
| `docs/test-strengthening.md:118` | `test-strengthening-plan.md` | Does not exist |
| `docs/test-strengthen-scheduler.md:109` | `guard-outside-project.py` hook as the safety net for `--dangerously-skip-permissions` | `.claude/settings.json` has **no `hooks` key at all** — a stated safety net that isn't there |
| `.claude/skills/bulk-import/SKILL.md:39` | `[the memory on import cleanup]` | Dangling link, no target |
| `docs/duplicate-detection-plan.md:114-143` | `app/dedup.py`, `scripts/dedup.py`, `content/.dedup-index.json` | None exist — *mitigated*, the doc labels itself a proposal |

### F.2 Factually wrong

**Breaks the first-run path:**

- **`HOST=0.0.0.0 uvicorn app.main:app` does not work.** **[V]** — uvicorn's CLI uses
  `auto_envvar_prefix="UVICORN"` (`uvicorn/main.py:61`), so it ignores `HOST`.
  `settings.HOST` is only read by `python -m app.main` (`app/main.py:88`). Following
  the README leaves the server on `127.0.0.1`. Wrong in **three** places:
  `README.md:45`, `CLAUDE.md:78`, `docs/tech-stack.md:14`. This is the README's
  headline use case.
- **`CONTRIBUTING.md:7`** instructs contributors to run `pnpm typecheck`, `pnpm lint`,
  `pnpm test`. There is no `package.json` and no JS toolchain. The guide's one
  actionable instruction is impossible to follow.
- **Setup contradiction:** `README.md:33` says `python3 -m venv .venv`;
  `CLAUDE.md:56-60` says a conda env at `./.venv` ("conda envs have no
  bin/activate"). `Makefile:4` sides with the README. Mutually exclusive instructions
  for the same directory.
- **`README.md:70-73`** claims `--content-dir` scopes `verify_bank.py`, `audit.py`,
  *and* `check_constraint_validators.py`. Only `verify_bank.py` has it (`:256`);
  `audit.py` has no argparse at all; `check_constraint_validators.py`'s positional
  arg means a flat staging dir, not a content root (`:79-82`).
- **`Makefile:13`** hardcodes `--host 10.8.0.1` (the owner's VPN IP) while
  `README.md:54` advertises `make run` as the generic LAN shortcut.

**Stale counts:** "741 problems" ×5 in `README.md` and once in
`docs/hint-generation.md:91` (actual: 738 / 435 / 1,173). "38-tag taxonomy" at
`README.md:17` (actual: 39 — and `README.md` is the *only* place that's wrong; see
F.4).

**Doc contradicts doc:**

- `docs/extended-problems.md:53-56` says `strengthen_tests.py` is "not (yet)
  extended-aware". It calls `content.load_all_roots()` at `:867` — it is.
  `CLAUDE.md:45` and `docs/test-strengthening.md:106` both say so.
- `docs/problem-generation.md:186-188` says `verify_json.py` "doesn't consume that
  layout directly". It does — `verify_json.py:22-31`, `:185-195`. `CLAUDE.md:42`
  describes it correctly.
- `docs/hint-generation.md:76` gives the model id as `qwen36`; the code default is
  `local-model` (`app/llm/hint_generator.py:45`).

**Wrong in the security-critical doc:** `docs/code-execution.md:14-33` lists four
non-negotiable "MUST" guarantees (isolated, network-disabled, unprivileged,
read-only FS) that the **shipped default backend violates all four of** — as the same
file admits ten lines later at `:42-43`. And `:92-103` still contains a
"pick one — Judge0 / Piston / e2b … **Recommendation for v1: start with Judge0
self-hosted to ship**" block, seven months after the executor was built. `:110` and
`docs/security.md:24` both claim tests "must pass in CI"; there is no test CI.

**Internally contradictory:** `docs/test-strengthening.md` describes the current
coverage-first model at `:9-48` and the **pre-rewrite** algorithm verbatim at
`:194-247` ("greedily select the minimal new cases that kill discriminators"). Both
are presented as current. `docs/user-accounts-v2.md:11-12` claims "the repo currently
has no git history"; `:33` cites a 35-test suite (now 91); `:142` recommends
argon2/bcrypt while `:41-42` of the same file correctly describes the shipped
`scrypt`.

### F.3 Stale

**`docs/roadmap.md` is the most stale doc in the repo** — last touched 2026-06-17,
missing ~6 weeks of shipped work. It marks pagination (`:22`, shipped:
`pages.py:533-539`) and bank growth (`:25`, shipped: 1,173 problems) as TODO, and
omits *everything* built since: progressive hints + the quality gate, the
test-strengthening engine, collections, class/design problems, input validators,
on-demand AI help, the extended content root, rich types, known/visit-later. Both
`README.md:25` and `CLAUDE.md:14` point readers at it as the status source.

`docs/tech-stack.md` still says "cookie-based, **no passwords**" (`:16`, `:29`) after
accounts-V2 shipped, and never mentions the OpenAI-compatible backend that hints, AI
help, and generation all use. `docs/architecture.md`'s component diagram (`:22-27`)
predates `testgen/`, `tags.py`, `auth.py`, `problem_validation.py`, `content.py`,
collections, and the SSE paths. `docs/api-design.md`, `docs/data-model.md`, and
`docs/PRD.md` all still contain literal `🔲 FILL OUT` placeholders — and
`docs/data-model.md:143`'s open question ("whether content/ files or the DB are the
source of truth") is definitively answered in `CLAUDE.md:88-89`.

`docs/adr/` contains one file: the template. `docs/adr/README.md:12-17` lists four
ADRs "to write soon" — all four decisions were made and are recorded as resolved in
`docs/tech-stack.md:20-32`. Meanwhile `docs/code-execution.md:33`, `:92`,
`docs/data-model.md:33`, and `CONTRIBUTING.md:22` all instruct the reader to "record
it in an ADR", a process nobody has executed.

### F.4 Agents and skills that corrupt authoring output

These are the highest-impact doc bugs, because an agent acts on them:

- **`.claude/skills/bulk-import/SKILL.md:30-34`** instructs skipping anything needing
  a class — "design a data structure … flag for owner decision rather than forcing a
  bad fit." Class/design problems have been first-class since commit `3cd8f44` and
  **88 exist**. The skill tells an agent to discard supported content.
- **`:29`** — its duplicate check covers `content/problems/` and
  `scripts/build_bank.py`, missing `content/problems-extended/` (435 problems,
  gitignored and therefore invisible to `git grep`) and the DB. This is exactly the
  failure mode `docs/extended-problems.md:58-65` warns about.
- **`:65-70`** routes authoring through the 15.6k-line `build_bank.py` monolith rather
  than the content-dir / `import_generated_problems.py` path, and never mentions
  `input_validator/`, hints, or the extended root.
- **`.claude/agents/problem-author.md:25`** says "reuse existing tags", contradicting
  the canonical-vocabulary rule at `CLAUDE.md:125-128`; it never mentions
  `app/tags.py` or `specs/tags.md`. `:22` mentions per-language starters in a
  Python-only app.
- `add-problem`, `new-problem-set`, and `problem-author` all omit
  `input_validator/input_validator.py` and `hints` from their required-pieces lists,
  though `specs/problem-schema.md:26-27` makes the validator mandatory.
- `.claude/commands/plan-feature.md:10-11` instructs citing `docs/data-model.md` and
  `docs/api-design.md` — the two least accurate docs in the repo.

Verified **healthy** (every flag checked against the source): `generated-problem-import`,
`test-strengthener`, `canonical-tags`, `test-all`.

### F.5 A TODO is being injected into the AI generator's prompt

`specs/problem-authoring-guidelines.md:106` contains a literal
`**TODO(owner):** add your requirements here.` plus two
`_(example — keep or replace)_` placeholders at `:103-105`. All three sit **inside**
the `AI-GUIDELINES:START/END` block (`:21`/`:108`) that `app/llm/generator.py:141-157`
injects verbatim into the model's system prompt. Every AI-generated problem is
currently authored against a TODO. The file's own comment at `:100-101` says "Delete
the examples once you've added your own."

The same file `:69-75` documents only `TreeNode` under "Solver contract" —
`ListNode` and `DoublyLinkedList` are absent, so the generator's injected guidelines
never mention two of the three rich types (both are documented elsewhere:
`specs/problem-schema.md:83-108`, `CLAUDE.md:106-110`).

### F.6 What the docs get right

Recorded so it isn't lost in the revamp:

- **The tag vocabulary is in perfect sync across four sources** — `app/tags.py`
  (39 canonical, 28 aliases, 2 dropped), `specs/tags.md`,
  `app/llm/problem_prompt.txt`, and `.claude/skills/canonical-tags/SKILL.md` all match
  exactly. `scripts/generate_problem_from_statement.py` even warns on drift. This is
  the one place the repo already does the right thing; a test should make it
  permanent (plan §2).
- `specs/problem-schema.md` is substantively accurate against `app/models.py` and
  `scripts/test_llm_output.py` — rich-type codecs, helper types, hint normalisation,
  and the class block all verified to match.
- `docs/importing-problems.md`, `docs/test-strengthen-scheduler.md`,
  `docs/input-validators.md`, `docs/design-problems.md`, and `docs/collections.md`
  are broadly reliable.
- The **in-flight doc changes are correct**: `git diff docs/ CLAUDE.md` (the LLM
  re-check feature) was verified against the code and is accurate and
  self-consistent.

### F.7 Structural gaps

- **The repo-layout table exists in three diverging copies** — `CLAUDE.md:25-51`
  (26 rows, most accurate), `README.md:79-95` (7 rows, contains a dead path),
  `docs/architecture.md:9-34` (2026-06 vintage).
- **No `docs/README.md` index and no `Status:` header on any doc**, so a reader cannot
  tell `importing-problems.md` (normative) from `api-design.md` (fiction) without
  reading both.
- **No CHANGELOG, no ADRs, no working CONTRIBUTING** — nothing forces a doc pass, which
  is why §F is this long (see E.5).
- **No end-to-end lifecycle doc.** `docs/architecture.md:36-49` covers run/score in
  five steps and is six weeks stale. Nothing documents the request lifecycle
  (startup/seed → identity middleware → list filtering → problem render → run → grade
  → persist → progress) or the content→DB→content round trip.
- **Undocumented entirely:** `app/templating.py`, `app/auth.py`, `app/config.py`, the
  front-end JS modules, the `known`/`visit-later` filters, `GET /random/{difficulty}`,
  the `tests/` suite, `scripts/seed_one.py`, `scripts/find_duplicate_slugs.py`,
  `staging/`, and the `JSONText` SQLite big-int affinity workaround
  (`app/models.py:180-183`) — which is subtle enough to have its own regression test
  and no prose at all.
- **No env-var reference.** `.env.example` exists, but no doc enumerates
  `LLM_GEN_BACKEND`, `LLM_HELP_*`, `EXEC_*`, `LOOTCODE_DB`, `EXEC_DOCKER_IMAGE`.
  `docs/ai-help.md:45-49` covers 3 of ~12.

---

## Appendix — metrics

| | |
|---|---:|
| Hand-written Python (app + scripts + tests) | 67 files / 34,526 LOC |
| `app/` | 35 files / 8,346 LOC |
| `scripts/` | 24 files / 24,828 LOC (`build_bank.py` alone: 15,594) |
| `tests/` | 8 files / 1,352 LOC / 91 tests |
| Test LOC as a share of app+scripts | **~4%** |
| Templates / static | 1,232 / 1,497 lines (+466 KB vendored `cm6.js`) |
| Problems (default / extended / DB) | 738 / 435 / 1,173 |
| `app/` return-annotation coverage | 74% (routers: 14–58%) |
| `# noqa` directives in `app/` using ruff codes | 37 |
| Loggers in `app/` | 1 |
| Routes / routes with a test | 33 / 11 |
| `app/` LOC with no runtime importer | ~2,900 (35%) |
| Markdown files / dead references / wrong claims | 26 / 14 / 22 |
| Commits / conforming to the mandated convention | 40 / 0 |
