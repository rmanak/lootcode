# Problem tag taxonomy

lootcode tags every problem from a **fixed canonical vocabulary** so the
browse/filter facets stay meaningful and near-synonyms don't multiply.

- **Authoritative source:** `app/tags.py` — `CANONICAL_TAGS`, `TAG_ALIASES`,
  `DROPPED_TAGS`, and `normalize_tags()`. This doc is prose; the code is law.
- **Authoring workflow:** the `canonical-tags` skill (`.claude/skills/canonical-tags/`).
- **Enforcement:** `app.content.write_problem_files` runs `normalize_tags` on
  every write (manual admin, AI generator, bulk-import generators), so aliases
  are corrected, dropped tags removed, and no problem is ever left tagless.

## Canonical tags (39)

| Group | Tags |
|---|---|
| Core data shapes | `array`, `string`, `matrix`, `linked-list`, `tree`, `binary-tree`, `graph` |
| Structures | `stack`, `monotonic-stack`, `queue`, `heap`, `hash-table`, `hash-set`, `hash-function`, `binary-search-tree`, `trie`, `union-find`, `binary-indexed-tree`, `suffix-array`, `design` |
| Techniques | `two-pointers`, `sliding-window`, `prefix-sum`, `binary-search`, `sorting`, `greedy`, `backtracking`, `recursion`, `divide-and-conquer`, `dynamic-programming`, `memoization`, `depth-first-search`, `breadth-first-search`, `bit-manipulation`, `bitmask` |
| Counting / numeric | `combinatorics`, `counting`, `simulation`, `math` |

`design` tags problems that ask you to **implement a data structure** driven by a
sequence of operations (the input is an operations list, e.g.
`["LRUCache", "put", "get", ...]` with per-op arguments; the harness/testgen
support this shape). Use it for the "build/design a structure" pattern, not for
one-shot computational problems.

`math` is a **catch-all umbrella**: kept only when no more specific canonical tag
applies (pure number-theory / geometry / probability / arithmetic-formula
problems), and used as the fallback so a problem is never tagless. When a
specific tag is present, the redundant `math` is stripped.

## Aliases (non-canonical → canonical)

Synonyms/abbreviations and too-detailed techniques fold up into a broader kept
category. Full map in `app/tags.py:TAG_ALIASES`:

- `bfs` → `breadth-first-search`; `dfs`, `flood-fill` → `depth-first-search`
- `hashing` → `hash-table`
- `bucket-sort`, `merge-sort`, `intervals`, `sweep-line` → `sorting`
- `monotonic-queue` → `queue`
- `ordered-set` → `binary-search-tree`; `segment-tree` → `binary-indexed-tree`
- `interval-dp`, `game-theory` → `dynamic-programming`
- `string-matching`, `rolling-hash` → `string`
- `dijkstra`, `bridges`, `eulerian-path`, `shortest-path`, `topological-sort`,
  `minimum-spanning-tree` → `graph`
- `number-theory`, `geometry`, `probability`, `probability-and-statistics` → `math`

## Dropped (removed entirely)

Too vague or a problem-type meta-tag with no good home: `enumeration`,
`queries`. Never use these.

## Extending the vocabulary

Don't invent tags inline. If a problem genuinely fits none of the canonical
tags, discuss with the owner first; if agreed, add the tag to `CANONICAL_TAGS`
in `app/tags.py`, document it here, and refresh the `canonical-tags` skill list.
