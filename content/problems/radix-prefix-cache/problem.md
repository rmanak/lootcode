LLM servers such as SGLang share the KV cache of common prompt prefixes (the
same system prompt, the same few-shot examples) between requests. They find
the shared part with a **radix tree** over token ids: a trie in which every
chain of single-child nodes is compressed into one edge labelled with a run of
tokens. Implement one.

- `RadixCache()` starts empty.
- `insert(sequence)` stores a non-empty token sequence. Storing a sequence that
  is already stored does nothing.
- `search(sequence)` returns `true` if exactly this sequence is stored, and
  `false` otherwise (a prefix of a stored sequence does not count).
- `prefixMatch(sequence)` returns the **longest stored sequence that is a
  prefix** of `sequence` (possibly all of it), or `[]` if no stored sequence is.
- `getAllSequences()` returns every stored sequence, sorted
  lexicographically (compare token by token; a proper prefix comes first).
- `structure()` describes the tree, so the tests can check that it really is
  compressed. Walk it depth-first from the root (which has no edge), visiting
  each node's children in increasing order of their edge's **first** token,
  and list every edge as `[depth, tokens]`, where `depth` is `1` for an edge
  out of the root. An empty tree gives `[]`.

**The tree must be compressed:** every node except the root either ends a
stored sequence or has at least two children. So inserting a sequence can
**split** an edge: with `[1, 2, 3, 4, 5]` stored (one edge), inserting
`[1, 2, 3]` splits it into `[1, 2, 3]` → `[4, 5]`, and inserting
`[1, 2, 9]` instead would split it into `[1, 2]` with children `[3, 4, 5]`
and `[9]`. (Because there are no deletions, this condition fixes the shape of
the tree completely, so `structure()` has one right answer.)

## Constraints

- Tokens are integers in `[0, 10⁶]`
- Inserted sequences have length `1` to `200`; queried ones `0` to `1000`
- At most `3000` calls, and at most `2·10⁵` tokens inserted in total

## Examples

**Example 1**

```
Input
["RadixCache", "insert", "insert", "insert", "structure", "getAllSequences"]
[[], [[10, 20]], [[1, 2, 3]], [[1, 2, 3, 4, 5, 6]], [], []]

Output
[null, null, null, null, [[1, [1, 2, 3]], [2, [4, 5, 6]], [1, [10, 20]]], [[1, 2, 3], [1, 2, 3, 4, 5, 6], [10, 20]]]
```

Explanation: the tree is

```
root
├── [1, 2, 3]        (stored)
│   └── [4, 5, 6]    (stored)
└── [10, 20]         (stored)
```

The root's children are listed by first token, so `[1, 2, 3]` (first token 1)
comes before `[10, 20]`.

**Example 2**

```
Input
["RadixCache", "insert", "insert", "insert", "structure", "insert", "insert", "structure"]
[[], [[1, 2, 3, 40, 50, 60, 70, 80]], [[1, 2, 3, 40, 50, 60, 700, 800]], [[1, 2, 3]], [],
 [[5]], [[1, 9]], []]

Output
[null, null, null, null, [[1, [1, 2, 3]], [2, [40, 50, 60]], [3, [70, 80]], [3, [700, 800]]],
 null, null, [[1, [1]], [2, [2, 3]], [3, [40, 50, 60]], [4, [70, 80]], [4, [700, 800]], [2, [9]], [1, [5]]]]
```

Explanation: the second insert splits the single edge after `60`. Inserting
`[1, 2, 3]` splits it again after `3`, and that node is marked as stored.
`[1, 9]` then splits the edge `[1, 2, 3]` right after its first token.

**Example 3**

```
Input
["RadixCache", "insert", "insert", "insert", "search", "search", "prefixMatch", "prefixMatch",
 "prefixMatch", "prefixMatch", "search"]
[[], [[1, 2, 3]], [[1, 2, 3, 4, 5]], [[10, 20]], [[1, 2]], [[1, 2, 3]], [[1, 2, 3, 4, 5, 6, 7]], [[1, 2]],
 [[1, 2, 3, 4]], [[99, 100]], [[]]]

Output
[null, null, null, null, false, true, [1, 2, 3, 4, 5], [], [1, 2, 3], [], false]
```

Explanation: `[1, 2]` is only a prefix of stored sequences, so `search` says
no, and no stored sequence is a prefix of it. The longest stored prefix of
`[1, 2, 3, 4]` is `[1, 2, 3]`: `[1, 2, 3, 4, 5]` is longer than the query. The
empty sequence is never stored.
