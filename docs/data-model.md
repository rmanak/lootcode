# Data model

> Conceptual entities. **Implemented** with SQLAlchemy in `app/models.py` on
> SQLite — that file is the source of truth; this doc is the high-level view.
> (The implemented model is a lean subset: User, Problem, TestCase, Submission,
> TestResult, KnownProblem; starters/canonical solution live as columns on Problem.)

## Entities

### User
A row is an anonymous **guest** by default (cookie-minted, no credentials) and
becomes an **account** once `username` + `password_hash` are set ("claiming" it,
in place — see `docs/user-accounts-v2.md`). The auth columns are nullable; NULLs
are exempt from the unique indexes, so all guests coexist.

| field | type | notes |
|-------|------|-------|
| id | uuid (pk) | also the value stored in the `lc_uid` cookie |
| name | string | display name (defaults to `guest`) |
| username | string? (unique) | login handle, lowercased; NULL ⇒ guest |
| email | string? (unique) | optional; for future password reset |
| password_hash | string? | stdlib-scrypt hash; NULL ⇒ unclaimed guest |
| claimed_at | timestamp? | when the row became an account |
| last_login_at | timestamp? | |
| createdAt | timestamp | |

> Not yet implemented: `role`/`is_admin` (admin is currently ungated) and
> `avatarUrl`. Tracked in `docs/user-accounts-v2.md` / `docs/roadmap.md`.

### Problem
> Authored content also lives as files in `content/problems/`; the DB row is the
> indexed/queryable copy. Decide sync direction (files → DB on deploy, or DB-only)
> and record it in an ADR.

| field | type | notes |
|-------|------|-------|
| id | uuid (pk) | |
| slug | string (unique) | matches `content/problems/<slug>` |
| title | string | |
| difficulty | enum(`easy`,`medium`,`hard`) | |
| tags | string[] | topics |
| statementMd | text | rendered problem.md |
| functionSpec | json | name, params, return (see problem-schema) |
| limits | json | timeLimitMs, memoryLimitMb |
| scoring | json | type + points/weights |
| isPublished | bool | |

### Language
| field | type | notes |
|-------|------|-------|
| id | string (pk) | e.g. `python`, `javascript` |
| displayName | string | |
| version | string | runtime version pinned in executor |

### Starter (per problem × language)
| field | type | notes |
|-------|------|-------|
| problemId | fk Problem | |
| languageId | fk Language | |
| code | text | starter stub shown in editor |

### TestCase
| field | type | notes |
|-------|------|-------|
| id | uuid (pk) | |
| problemId | fk Problem | |
| name | string | |
| input | json | |
| expected | json | |
| weight | int | for weighted scoring |
| isHidden | bool | hidden tests run only on submit |

### Submission
| field | type | notes |
|-------|------|-------|
| id | uuid (pk) | |
| userId | fk User | |
| problemId | fk Problem | |
| languageId | fk Language | |
| code | text | the submitted source (private) |
| kind | enum(`run`,`submit`) | run = visible tests only |
| status | enum(`queued`,`running`,`done`,`error`) | |
| score | int | computed |
| passedCount / totalCount | int | |
| runtimeMs / memoryKb | int? | aggregate |
| createdAt | timestamp | |

### TestResult (per submission × test)
| field | type | notes |
|-------|------|-------|
| submissionId | fk Submission | |
| testCaseId | fk TestCase | |
| passed | bool | |
| stdout / stderr | text? | size-capped |
| runtimeMs / memoryKb | int? | |

### KnownProblem (implemented)
A user's explicit "I already know this — stop surfacing it" mark on a problem.
Independent of `solved` (which is derived from Submissions): a problem can be
known without ever being solved.

| field | type | notes |
|-------|------|-------|
| id | int (pk) | |
| userId | fk User | |
| problemId | fk Problem | unique together with userId |
| createdAt | timestamp | |

> **Solved ⇒ known** is a *UI* rule, not stored here: the "unknown only" filter
> and the random "next" picks hide solved problems too, but solving never writes
> a KnownProblem row. Marking known is reversible (the row is deleted on unmark).

### VisitLaterProblem (implemented)
A user's "bookmark to come back to this" mark — the opposite intent of
KnownProblem. Independent of both `solved` and `known`, and never auto-cleared:
it's a pure explicit record, surfaced by the "Visit later" filter on the problem
list (an independent axis that combines with every other filter).

| field | type | notes |
|-------|------|-------|
| id | int (pk) | |
| userId | fk User | |
| problemId | fk Problem | unique together with userId |
| createdAt | timestamp | |

> Unlike "known", flagging "visit later" does **not** hide the problem from the
> random "next" picks — it's a reminder, not a dismissal. Reversible (the row is
> deleted on unflag).

### Progress (derived, optional)
Per `(userId, problemId)`: best status (`solved`/`attempted`), best score,
firstSolvedAt. Can be a materialized view over Submission.

## Relationships

```
User 1───* Submission *───1 Problem 1───* TestCase
                 │                   1───* Starter *───1 Language
                 *
             TestResult
```

🔲 FILL OUT — confirm scoring fields, whether `content/` files or the DB are the
source of truth for problems, and any extra entities (teams, contests, plans).
