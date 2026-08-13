# Problem tag taxonomy

lootcode tags every problem from a **fixed canonical vocabulary** so the
browse/filter facets stay meaningful and near-synonyms don't multiply.

- **Authoritative source:** `app/tags.py` — `CANONICAL_TAGS`, `TAG_ALIASES`,
  `DROPPED_TAGS`, and `normalize_tags()`. This doc is prose; the code is law.
- **Authoring workflow:** the `canonical-tags` skill (`.claude/skills/canonical-tags/`).
- **Enforcement:** `app.content.write_problem_files` runs `normalize_tags` on
  every write (manual admin, AI generator, bulk-import generators), so aliases
  are corrected, dropped tags removed, and no problem is ever left tagless.

## Canonical tags (44)

| Group | Tags |
|---|---|
| Core data shapes | `array`, `string`, `matrix`, `linked-list`, `tree`, `binary-tree`, `graph` |
| Structures | `stack`, `monotonic-stack`, `queue`, `heap`, `hash-table`, `hash-function`, `binary-search-tree`, `ordered-set`, `trie`, `union-find`, `binary-indexed-tree`, `segment-tree`, `suffix-array`, `design` |
| Techniques | `two-pointers`, `sliding-window`, `prefix-sum`, `binary-search`, `sorting`, `greedy`, `backtracking`, `recursion`, `divide-and-conquer`, `dynamic-programming`, `memoization`, `depth-first-search`, `breadth-first-search`, `topological-sort`, `shortest-path`, `bit-manipulation`, `bitmask` |
| Counting / numeric | `combinatorics`, `counting`, `simulation`, `number-theory`, `geometry`, `math` |

`design` tags problems that ask you to **implement a data structure** driven by a
sequence of operations (the input is an operations list, e.g.
`["LRUCache", "put", "get", ...]` with per-op arguments; the harness
support this shape). Use it for the "build/design a structure" pattern, not for
one-shot computational problems.

`math` is a **catch-all umbrella**: kept only when no more specific canonical tag
applies (arithmetic-formula and probability problems), and used as the fallback so
a problem is never tagless. When a specific tag is present — including the two
that were split out of it, `number-theory` and `geometry` — the redundant `math`
is stripped.

Three more pairs are deliberately kept **apart** rather than folded together:
`binary-indexed-tree` vs `segment-tree` (different structures), `binary-search-tree`
vs `ordered-set` (a BST as the problem's subject vs a sorted container used as a
tool), and `graph` vs its two named techniques `topological-sort` and
`shortest-path`.

## Aliases (non-canonical → canonical)

Synonyms/abbreviations and too-detailed techniques fold up into a broader kept
category. Full map in `app/tags.py:TAG_ALIASES`:

- `bfs` → `breadth-first-search`; `dfs`, `flood-fill` → `depth-first-search`
- `hashing`, `hash-set` → `hash-table`
- `bucket-sort`, `counting-sort`, `radix-sort`, `quickselect`, `merge-sort`,
  `interval`, `intervals`, `sweep-line`, `line-sweep` → `sorting`
- `monotonic-queue` → `queue`; `heap-priority-queue`, `priority-queue` → `heap`
- `doubly-linked-list` → `linked-list`
- `data-stream`, `iterator` → `design`
- `interval-dp`, `game-theory` → `dynamic-programming`
- `string-matching`, `rolling-hash` → `string`
- `biconnected-component`, `bridges`, `eulerian-path`, `eulerian-circuit`,
  `minimum-spanning-tree` → `graph`; `dijkstra` → `shortest-path`
- `probability`, `probability-and-statistics` → `math`

## Dropped (removed entirely)

Too vague or a problem-type meta-tag with no good home: `enumeration`, `queries`,
`brainteaser`. Also dropped are tags that describe how a problem is *delivered*
rather than how it is solved — `database`, `shell` and `concurrency` name a
language we don't run, and `interactive`, `randomized` and `reservoir-sampling`
name a judging style we re-author away. Never use these.

## Extending the vocabulary

Don't invent tags inline. If a problem genuinely fits none of the canonical
tags, discuss with the owner first; if agreed, add the tag to `CANONICAL_TAGS`
in `app/tags.py`, document it here, and refresh the `canonical-tags` skill list.
