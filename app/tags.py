"""Canonical problem-tag taxonomy — the single source of truth for `tags`.

Every problem in the bank is tagged from a fixed, curated vocabulary so that
filtering stays meaningful and duplicates/near-synonyms don't proliferate
(`bfs` vs `breadth-first-search`, `monotonic-queue` vs `queue`, ...).

Three pieces:
  * ``CANONICAL_TAGS`` — the allowed vocabulary. Nothing else should be stored.
  * ``TAG_ALIASES``    — non-canonical tag -> canonical tag (merge / fold-up).
  * ``DROPPED_TAGS``   — tags removed entirely (too vague / meta, no good home).

``normalize_tags`` applies all three and is wired into
``app.content.write_problem_files``, so *every* write path (manual admin,
AI generator, bulk-import generators) lands canonical tags on disk.

``math`` is a deliberate **catch-all umbrella**: it is kept only when a problem
has no more specific canonical tag, and is the fallback for an otherwise
tagless problem. See ``specs/tags.md`` for the prose taxonomy and rationale,
and the ``canonical-tags`` skill for the authoring workflow.
"""
from __future__ import annotations

# The umbrella catch-all (kept only when nothing more specific applies).
MATH = "math"

# Allowed vocabulary (38 tags). Keep alphabetised.
CANONICAL_TAGS: frozenset[str] = frozenset({
    "array",
    "backtracking",
    "binary-indexed-tree",
    "binary-search",
    "binary-search-tree",
    "binary-tree",
    "bit-manipulation",
    "bitmask",
    "breadth-first-search",
    "combinatorics",
    "counting",
    "depth-first-search",
    "divide-and-conquer",
    "dynamic-programming",
    "graph",
    "greedy",
    "hash-function",
    "hash-set",
    "hash-table",
    "heap",
    "linked-list",
    "math",
    "matrix",
    "memoization",
    "monotonic-stack",
    "prefix-sum",
    "queue",
    "recursion",
    "simulation",
    "sliding-window",
    "sorting",
    "stack",
    "string",
    "suffix-array",
    "tree",
    "trie",
    "two-pointers",
    "union-find",
})

# Non-canonical tag -> canonical tag. Synonyms/abbreviations and too-detailed
# techniques folded up into a broader kept category. The math family
# (number-theory / geometry / probability*) folds into the ``math`` umbrella.
TAG_ALIASES: dict[str, str] = {
    "bfs": "breadth-first-search",
    "dfs": "depth-first-search",
    "hashing": "hash-table",
    "bucket-sort": "sorting",
    "merge-sort": "sorting",
    "intervals": "sorting",
    "sweep-line": "sorting",
    "monotonic-queue": "queue",
    "ordered-set": "binary-search-tree",
    "segment-tree": "binary-indexed-tree",
    "interval-dp": "dynamic-programming",
    "game-theory": "dynamic-programming",
    "flood-fill": "depth-first-search",
    "string-matching": "string",
    "rolling-hash": "string",
    "bridges": "graph",
    "dijkstra": "graph",
    "shortest-path": "graph",
    "eulerian-path": "graph",
    "minimum-spanning-tree": "graph",
    "topological-sort": "graph",
    "number-theory": "math",
    "geometry": "math",
    "probability": "math",
    "probability-and-statistics": "math",
}

# Tags removed entirely: too vague / a problem-type meta-tag, with no good home.
DROPPED_TAGS: frozenset[str] = frozenset({
    "design",
    "enumeration",
    "queries",
})


def normalize_tags(raw: list[str] | None) -> list[str]:
    """Map an arbitrary tag list onto the canonical vocabulary.

    Applies aliases, removes dropped tags, de-duplicates while preserving order,
    keeps ``math`` only as a fallback umbrella, and guarantees a non-empty
    result (a problem is never left tagless). Unknown tags (not canonical, not
    an alias, not dropped) are passed through unchanged so nothing is silently
    lost — use :func:`unknown_tags` to detect and surface them.
    """
    out: list[str] = []
    for tag in raw or []:
        t = (tag or "").strip().lower()
        if not t or t in DROPPED_TAGS:
            continue
        t = TAG_ALIASES.get(t, t)
        if t not in out:
            out.append(t)
    # ``math`` is an umbrella catch-all: drop it when something more specific applies.
    if MATH in out and len(out) > 1:
        out = [t for t in out if t != MATH]
    # Never leave a problem with no tag.
    if not out:
        out = [MATH]
    return out


def unknown_tags(raw: list[str] | None) -> list[str]:
    """Return tags that are neither canonical, a known alias, nor dropped.

    These are exactly the tags an author should *not* invent on their own: if a
    problem genuinely needs one, the canonical vocabulary should be extended
    here on purpose (see the ``canonical-tags`` skill) rather than ad hoc.
    """
    seen: list[str] = []
    for tag in raw or []:
        t = (tag or "").strip().lower()
        if not t:
            continue
        if t in CANONICAL_TAGS or t in TAG_ALIASES or t in DROPPED_TAGS:
            continue
        if t not in seen:
            seen.append(t)
    return seen


def is_canonical(tag: str) -> bool:
    return (tag or "").strip().lower() in CANONICAL_TAGS
