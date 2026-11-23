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

# Allowed vocabulary (62 tags). Keep alphabetised.
CANONICAL_TAGS: frozenset[str] = frozenset({
    "array",
    "backpropagation",
    "backtracking",
    "binary-indexed-tree",
    "binary-search",
    "binary-search-tree",
    "binary-tree",
    "bit-manipulation",
    "bitmask",
    "breadth-first-search",
    "classical-ml",
    "combinatorics",
    "computer-vision",
    "counting",
    "data-preprocessing",
    "decoding",
    "depth-first-search",
    "design",
    "divide-and-conquer",
    "dynamic-programming",
    "evaluation-metrics",
    "geometry",
    "graph",
    "greedy",
    "hash-function",
    "hash-table",
    "heap",
    "linear-algebra",
    "linked-list",
    "llm-apps",
    "llm-inference",
    "loss-function",
    "machine-learning",
    "math",
    "matrix",
    "memoization",
    "monotonic-stack",
    "neural-networks",
    "nlp",
    "number-theory",
    "optimization",
    "ordered-set",
    "prefix-sum",
    "pytorch",
    "queue",
    "recursion",
    "reinforcement-learning",
    "segment-tree",
    "shortest-path",
    "simulation",
    "sliding-window",
    "sorting",
    "stack",
    "statistics",
    "string",
    "suffix-array",
    "topological-sort",
    "transformer",
    "tree",
    "trie",
    "two-pointers",
    "union-find",
})

# The machine-learning *topic* tags: a sub-vocabulary that only ever appears
# next to the ``machine-learning`` domain tag, so the ML problems (otherwise a
# single 100-problem bucket) can be filtered by what they practise. Every ML
# problem carries 1-3 of them; tests/test_tags.py pins both halves of that.
ML_TOPIC_TAGS: frozenset[str] = frozenset({
    "backpropagation",
    "classical-ml",
    "computer-vision",
    "data-preprocessing",
    "decoding",
    "evaluation-metrics",
    "linear-algebra",
    "llm-apps",
    "llm-inference",
    "loss-function",
    "neural-networks",
    "nlp",
    "optimization",
    "reinforcement-learning",
    "statistics",
    "transformer",
})

# The machine-learning *framework* tags: which library a problem is solved in,
# not what it practises, so they sit outside ML_TOPIC_TAGS and do not count
# toward an ML problem's 1-3 topic tags. Like the topic tags they only appear
# next to ``machine-learning``. A problem tagged ``pytorch`` is exactly one that
# runs on the PyTorch runtime (``"runtime": "torch"``); without the tag an ML
# problem is a numpy one. tests/test_tags.py pins both rules over the bank, and
# docs/pytorch-twins.md says how a PyTorch twin of a numpy problem is built.
ML_FRAMEWORK_TAGS: frozenset[str] = frozenset({
    "pytorch",
})

# Non-canonical tag -> canonical tag. Synonyms/abbreviations and too-detailed
# techniques folded up into a broader kept category.
TAG_ALIASES: dict[str, str] = {
    "bfs": "breadth-first-search",
    "dfs": "depth-first-search",
    "hashing": "hash-table",
    "hash-set": "hash-table",
    "bucket-sort": "sorting",
    "counting-sort": "sorting",
    "merge-sort": "sorting",
    "radix-sort": "sorting",
    "quickselect": "sorting",
    "interval": "sorting",
    "intervals": "sorting",
    "sweep-line": "sorting",
    "line-sweep": "sorting",
    "monotonic-queue": "queue",
    "heap-priority-queue": "heap",
    "priority-queue": "heap",
    "doubly-linked-list": "linked-list",
    "data-stream": "design",
    "iterator": "design",
    "interval-dp": "dynamic-programming",
    "game-theory": "dynamic-programming",
    "flood-fill": "depth-first-search",
    "string-matching": "string",
    "rolling-hash": "string",
    "biconnected-component": "graph",
    "bridges": "graph",
    "eulerian-circuit": "graph",
    "eulerian-path": "graph",
    "minimum-spanning-tree": "graph",
    "dijkstra": "shortest-path",
    "probability": "math",
    "probability-and-statistics": "math",
    "ml": "machine-learning",
    "deep-learning": "machine-learning",
    "neural-network": "machine-learning",
    "torch": "pytorch",
}

# Tags removed entirely: too vague / a problem-type meta-tag, or describing how a
# problem is *delivered* rather than how it is solved (`database`, `shell` and
# `concurrency` name a language we don't run; `interactive` and `randomized` name
# a judging style we re-author away). No good home in the vocabulary.
DROPPED_TAGS: frozenset[str] = frozenset({
    "brainteaser",
    "concurrency",
    "database",
    "enumeration",
    "interactive",
    "queries",
    "randomized",
    "reservoir-sampling",
    "shell",
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
