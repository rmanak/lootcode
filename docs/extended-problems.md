# Extended (extra) problem set

The problem bank is split across two roots:

| Root | Committed? | What it holds |
|------|-----------|----------------|
| `content/problems/` | yes | The **default** set — everything shipped in the repo. |
| `content/problems-extended/` | **no** (gitignored) | An optional **extended** set of extra problems kept local, not pushed to GitHub. |

Both roots have the same on-disk layout (`<slug>/meta.json`, `tests/`, …; see
`specs/problem-schema.md`) and are **seeded together** into the same DB. Slugs
must be unique across the two — a problem lives in exactly one root, and seeding
upserts by slug.

A fresh `git clone` gets only the default set. The extended problems — and any
collection reference to them — simply **drop**, with no error. This is by design.

## How dropping stays safe

- `settings.content_dirs` lists both roots; `store.seed_from_content` loads each,
  and `content.load_all` skips a root that doesn't exist. So a clone with no
  `content/problems-extended/` seeds the default set alone.
- Collections (`content/collections/*.json`) reference problems by slug.
  `store.seed_collections` resolves each slug to a problem id and **skips**
  unknown ones (they never crash seeding). So *Blind 73* etc. just render with
  fewer members when some live in the (absent) extended set.
- The listing page filters by DB membership, so a dropped problem is simply not a
  member — no dangling links, no empty pages.
- `scripts/seed.py` **reports** skipped collection references but treats them as
  non-fatal (exit 0). A genuine typo in a manifest shows up in that same list, so
  glance at it when editing collections.

## Moving a problem into (or out of) the extended set

1. Move the directory: `mv content/problems/<slug> content/problems-extended/<slug>`
   (the destination is gitignored). Reverse the direction to bring one back.
2. Re-run `python scripts/seed.py` (or restart the app) to reseed.

New problems authored via the app or `/add-problem` are written to the default
`content/problems/` root; move them afterward if you want them extended.
