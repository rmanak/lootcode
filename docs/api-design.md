# API design (draft)

> **As implemented (V1):** the UI is server-rendered, so the only JSON endpoint is
> `POST /api/problems/{slug}/run` (runs all tests + scores; see
> `app/routers/submissions.py`). Pages `/`, `/problems/{slug}`, `/me`, `/admin`
> return HTML. The fuller REST sketch below is kept as design reference for when an
> API/SPA split is wanted.

## Conventions

- Base path `/api/v1`. Errors: `{ "error": { "code", "message" } }`.
- List endpoints are paginated: `?page`, `?limit`, return `{ items, total }`.

## Problems

```
GET  /api/v1/problems?difficulty=&tag=&q=&page=     list/search (public)
GET  /api/v1/problems/:slug                          full statement + starters
                                                     (visible tests only; never
                                                     returns hidden tests)
```

## Submissions

```
POST /api/v1/problems/:slug/run                      run vs VISIBLE tests
       body: { languageId, code }
       → 202 { submissionId }

POST /api/v1/problems/:slug/submit                   run vs ALL tests, scores
       body: { languageId, code }
       → 202 { submissionId }

GET  /api/v1/submissions/:id                         poll status + results
       → { status, score, passedCount, totalCount, results[], runtimeMs }
```

> Runs are async (queued → executor). Client polls `GET /submissions/:id`, or
> subscribe via SSE/WebSocket: `GET /api/v1/submissions/:id/stream`.

## User / progress

```
GET  /api/v1/me                                      current user
GET  /api/v1/me/submissions?problemSlug=             history
GET  /api/v1/me/progress                             solved/attempted summary
```

## Auth

```
GET  /api/v1/auth/session
POST /api/v1/auth/signout
# OAuth sign-in handled by Auth.js routes
```

## Authoring (role: author/admin)

```
POST /api/v1/admin/problems                          create/import from content/
PUT  /api/v1/admin/problems/:slug
POST /api/v1/admin/problems/:slug/publish
```

🔲 FILL OUT — confirm protocol (REST vs tRPC/GraphQL), pagination shape, and the
realtime mechanism (poll vs SSE vs WebSocket).
