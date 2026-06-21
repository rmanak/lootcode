# Problem collections (curated lists)

A **collection** is a curated, system-defined list of problems — e.g. *Blind 73*,
or a future *Top 150 Interview*. Collections are a **filter** on the problem list
(`/?collection=<slug>`): selecting one narrows the bank to that list's members,
shown in the list's curated **study order**.

These are shipped with the app and edited by maintainers. There are **no
user-defined collections** (no UI/admin to create them) — membership lives in
version-controlled content, like problems and tags.

## On disk

One JSON manifest per list under `content/collections/<slug>.json`:

```json
{
  "slug": "blind-73",
  "title": "Blind 73",
  "subtitle": "Short one-line description shown in the banner.",
  "problems": ["two-sum", "valid-anagram", "..."]
}
```

- `slug` — kebab-case, unique, matches the filename and the `?collection=` value.
- `title` — display name (chip + banner).
- `subtitle` — optional one-liner shown in the banner.
- `problems` — problem **slugs** in canonical study order. Order is preserved as
  each member's `position` and is how the list renders when active.

## How it loads

1. `app/content.py:load_collections()` reads every `content/collections/*.json`
   (returns `[]` if the directory is absent, so older checkouts are unaffected).
2. `app/store.py:seed_collections()` upserts a `Collection` row per manifest and
   rebuilds its `CollectionProblem` membership, resolving each slug to a
   `Problem.id` in manifest order. It runs on every app startup (idempotent) and
   from `scripts/seed.py`.
3. The list filter lives in `app/routers/pages.py:index()` (mirrors the `topic`
   filter); the "Lists" chips + active-list banner are in
   `app/templates/index.html`.

### Unknown slugs

A slug that doesn't match a problem (a typo, or a problem not yet in the bank) is
**skipped, not fatal**: `seed_collections` returns the unresolved `<list>:<slug>`
refs, `scripts/seed.py` prints them, and `scripts/audit.py` **fails** on any —
so a bad slug can't silently drop a problem from a list. Keep audit green.

## Adding a new list

1. Drop a new `content/collections/<slug>.json` manifest (slugs must already exist
   in `content/problems/`, or be added alongside).
2. `python scripts/seed.py` — seeds the list and reports any unresolved slugs.
3. `python scripts/audit.py` — must stay green (every slug resolves).

The new list automatically appears as a "Lists" chip on the problem page; no code
change is needed.
