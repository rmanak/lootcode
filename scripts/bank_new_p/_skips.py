"""Intentionally-skipped new_p.txt slugs (these are never authored).

Two reasons land a slug here:
  * **duplicate** — the same LeetCode problem already exists in the bank under a
    *different* slug, so the slug-based dedup in `_worklist` missed it; or
  * **doesn't fit** — the task is not a single pure-function solver (stateful
    design class, serialize/deserialize codec, interactive guess API, iterator),
    and can't be honestly reframed into one.

`_worklist.pending()` subtracts these so the marathon can reach a clean zero
instead of stalling on a residue of un-authorable entries. The value is a short
human reason (for the record only).
"""

SKIP = {
    # --- duplicates of an existing bank problem under a different slug ---
    "path-with-maximum-probability": "dup of maximum-probability-path",
    "kth-largest-element-in-an-array": "dup of kth-largest-element",
    "task-scheduler": "dup of task-scheduler-cooldown",
    "partition-array-for-maximum-sum": "dup of partition-array-max-sum",
    "candy": "dup of candy-distribution",
    "longest-substring-without-repeating-characters": "dup of longest-substring-without-repeating",
    "search-a-2d-matrix": "dup of search-sorted-matrix",
    "find-the-duplicate-number": "dup of find-duplicate-number",
    "largest-component-size-by-common-factor": "dup of largest-component-common-factor",
    "regular-expression-matching": "dup of regex-full-match",
    "word-ladder": "dup of word-ladder-length",
    "divide-array-in-sets-of-k-consecutive-numbers": "dup of hand-of-straights",
    "find-minimum-in-rotated-sorted-array": "dup of find-minimum-rotated-sorted",
    "palindrome-partitioning-ii": "dup of palindrome-partition-min-cuts",
    "minimum-cost-tree-from-leaf-values": "dup of min-cost-tree-leaf-values",
    "maximum-profit-in-job-scheduling": "dup of maximum-profit-job-scheduling",
    "product-of-array-except-self": "dup of product-except-self",
    "count-good-nodes-in-binary-tree": "dup of count-good-nodes (goodNodes)",
    "smallest-subtree-with-all-the-deepest-nodes": "dup of lowest-common-ancestor-of-deepest-leaves",
    "unique-binary-search-trees-ii": "return all BST shapes; the count is dup of unique-binary-search-trees",
    # --- return-any / not a single gradable answer ---
    "string-without-aaa-or-bbb": "return any valid string; longest length is trivially A+B",
    "pancake-sorting": "return any valid flip sequence; not a single gradable answer",
    "beautiful-array": "return any beautiful permutation; not a single gradable answer",
    # --- stateful / interactive design (not a single pure function) ---
    "random-pick-index": "stateful design class + random output; not single-answer gradable",
    "insert-delete-getrandom-o1": "stateful design class + random output; not single-answer gradable",
    "insert-delete-getrandom-o1-duplicates-allowed": "stateful design class + random output; not single-answer gradable",
    "all-oone-data-structure": "stateful design class (inc/dec/getMax/getMin); not a single pure function",
    "subrectangle-queries": "stateful design class (update/get); not a single pure function",
    "range-sum-query-mutable": "stateful design class (update/sumRange); not a single pure function",
    "word-ladder-ii": "return all shortest transformation sequences; length is dup of word-ladder-length",
    # --- batch 022 ---
    "sort-list": "sort a linked list; reframed to an array == existing sort-an-array",
    "course-schedule-ii": "lexicographically-smallest topo order == existing course-schedule-ordering",
    "time-based-key-value-store": "dup of existing time-based-kv-store (batch get/set replay)",
    "find-a-corresponding-node-of-a-binary-tree-in-a-clone-of-that-tree": "returns a node pointer in a clone; meaningless in our array repr",
    "dinner-plate-stacks": "stateful design class (push/pop/popAtStack); not a single pure function",
    "mini-parser": "deserialize a NestedInteger codec; not a single-answer gradable function",
}
