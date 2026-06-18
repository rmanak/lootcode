---
name: canonical-tags
description: Assign problem `tags` from lootcode's fixed canonical vocabulary. Use whenever you author, import, or edit a problem's tags (single add, bulk import, or themed set) — pick only canonical tags, and if a problem fits none, stop and discuss adding a new one rather than inventing a tag.
---

Tag every problem from the **canonical vocabulary** below — nothing else. This
keeps the browse/filter facets meaningful and stops near-synonyms
(`bfs`/`breadth-first-search`, `monotonic-stack`/`stack`, `math`/`number-theory`)
from multiplying.

The authoritative machine-readable source is **`app/tags.py`**
(`CANONICAL_TAGS`, `TAG_ALIASES`, `DROPPED_TAGS`, `normalize_tags`). The prose
taxonomy + rationale is **`specs/tags.md`**. This skill is the authoring
workflow. If those files and this list ever disagree, `app/tags.py` wins — refresh
this skill from it.

## Canonical tags (37)

Pick **1–4** that best describe the *technique/structure*, not incidental detail.

- **Core data shapes:** `array` · `string` · `matrix` · `linked-list` · `tree` ·
  `binary-tree` · `graph`
- **Structures:** `stack` · `queue` · `heap` · `hash-table` · `hash-set` ·
  `hash-function` · `binary-search-tree` · `trie` · `union-find` ·
  `binary-indexed-tree` · `suffix-array`
- **Techniques:** `two-pointers` · `sliding-window` · `prefix-sum` ·
  `binary-search` · `sorting` · `greedy` · `backtracking` · `recursion` ·
  `divide-and-conquer` · `dynamic-programming` · `memoization` ·
  `depth-first-search` · `breadth-first-search` · `bit-manipulation` · `bitmask`
- **Counting / numeric:** `combinatorics` · `counting` · `simulation` · `math`

`math` is a **catch-all umbrella** — use it only when no more specific tag
applies (pure number-theory / geometry / probability / arithmetic-formula
problems). If a problem already has a specific tag, do **not** also add `math`;
`normalize_tags` strips the redundant umbrella anyway.

## Don't use these — they map to a canonical tag

Common aliases (full map in `app/tags.py:TAG_ALIASES`):

| Instead of… | use |
|---|---|
| `bfs` | `breadth-first-search` |
| `dfs`, `flood-fill` | `depth-first-search` |
| `hashing` | `hash-table` |
| `bucket-sort`, `merge-sort`, `intervals`, `sweep-line` | `sorting` |
| `monotonic-stack` | `stack` |
| `monotonic-queue` | `queue` |
| `ordered-set` | `binary-search-tree` |
| `segment-tree` | `binary-indexed-tree` |
| `interval-dp`, `game-theory` | `dynamic-programming` |
| `string-matching`, `rolling-hash` | `string` |
| `dijkstra`, `bridges`, `eulerian-path`, `shortest-path`, `topological-sort`, `minimum-spanning-tree` | `graph` |
| `number-theory`, `geometry`, `probability`, `probability-and-statistics` | `math` |

**Dropped entirely** (never use): `design`, `enumeration`, `queries`.

## Workflow

1. Choose the 1–4 canonical tags that best fit the problem's core idea.
2. **If nothing fits** (the problem is genuinely a category the vocabulary
   doesn't cover): **stop and come back to the user** to discuss adding a new
   canonical tag. Do **not** invent a tag inline — a one-off tag defeats the
   point. If the user agrees, add it to `CANONICAL_TAGS` in `app/tags.py`, note
   it in `specs/tags.md`, refresh the list above, then proceed.
3. Validate before finishing:

   ```bash
   python -c "import sys; from app.tags import normalize_tags, unknown_tags; \
   t=sys.argv[1].split(','); u=unknown_tags(t); \
   print('normalized:', normalize_tags(t)); \
   print('UNKNOWN -> discuss before using:', u) if u else print('all canonical OK')" \
   "array,depth-first-search"
   ```

   `unknown_tags(...)` returning anything is the signal from step 2 — resolve it
   with the user, don't ship it.

`app.content.write_problem_files` runs `normalize_tags` on every write, so
aliases/dropped tags are corrected and no problem is ever left tagless. That's a
safety net, **not** a license to be sloppy — choose canonical tags deliberately
so the stored set reflects intent, not the normalizer's best guess.
