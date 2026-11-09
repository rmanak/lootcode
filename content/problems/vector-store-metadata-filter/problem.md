Semantic code search embeds every chunk of a codebase as a vector and, for a
query, returns the most similar chunks, often restricted by metadata ("only
Python files"). Build the in-memory store behind it.

- `VectorStore(dim)` creates an empty store for vectors of length `dim`.
- `upsert(id, vector, metadata)` stores a record. If `id` is already stored,
  its vector and metadata are **replaced**.
- `delete(id)` removes a record; deleting an unknown id does nothing.
- `query(vector, topK, filter)` returns the best matches, described below.
- `size()` returns the number of stored records.

**Query.** A record **matches** `filter` when every key in `filter` is present
in its metadata with exactly that value (an empty filter matches everything).
Score every matching record by **cosine similarity** with the query:

$$
\cos(q, v) = \frac{q \cdot v}{\lVert q \rVert \, \lVert v \rVert}
$$

defined as $0$ when either vector is all zeros. Return the `topK` best as
`[id, score, metadata]` entries, by score from highest to lowest, with ties
broken by `id` in increasing string order. If fewer than `topK` records match,
return all of them.

Records only tie in the tests when their scores are equal however they are
computed (a zero vector's score of $0$, for example); otherwise the scores of
two matching records differ by at least $10^{-9}$, so the order is well
defined.

A store can hold thousands of records and serve hundreds of queries; score
all candidates at once (a matrix-vector product over normalized vectors) and
select the top ones with a heap or a partial sort, rather than sorting
everything in Python for every query.

You may use **numpy** and the Python standard library.

## Constraints

- `1 <= dim <= 256`; every vector has `dim` finite numbers with absolute value `<= 100`
- Ids are non-empty strings of at most `20` characters
- Metadata and filters have at most `5` string keys, with string or integer values
- `1 <= topK <= 50`; at most `3000` calls in total

## Examples

**Example 1**

```
Input
["VectorStore", "upsert", "upsert", "upsert", "query", "query"]
[[4], ["chunk_1", [0.1, 0.9, 0.0, 0.3], {"file": "main.py", "language": "python"}],
 ["chunk_2", [0.8, 0.1, 0.5, 0.0], {"file": "utils.ts", "language": "typescript"}],
 ["chunk_3", [0.1, 0.85, 0.1, 0.25], {"file": "helper.py", "language": "python"}],
 [[0.1, 0.9, 0.0, 0.3], 2, {"language": "python"}], [[1.0, 0.0, 0.0, 0.0], 1, {}]]

Output
[null, null, null, null,
 [["chunk_1", 1.0, {"file": "main.py", "language": "python"}],
  ["chunk_3", 0.9931167101330015, {"file": "helper.py", "language": "python"}]],
 [["chunk_2", 0.8432740427115678, {"file": "utils.ts", "language": "typescript"}]]]
```

Explanation: the filter leaves the two Python chunks, and the query is
`chunk_1`'s own vector. The second query has no filter; `chunk_2` points
most nearly along the first axis.

**Example 2**

```
Input
["VectorStore", "upsert", "upsert", "upsert", "query", "upsert", "delete", "size", "query"]
[[2], ["b", [1.0, 0.0], {}], ["a", [2.0, 0.0], {"x": 1}], ["c", [0.0, 0.0], {}], [[3.0, 0.0], 5, {}],
 ["a", [0.0, -1.0], {}], ["zzz"], [], [[3.0, 0.0], 5, {}]]

Output
[null, null, null, null, [["a", 1.0, {"x": 1}], ["b", 1.0, {}], ["c", 0.0, {}]], null, null, 3,
 [["b", 1.0, {}], ["a", 0.0, {}], ["c", 0.0, {}]]]
```

Explanation: `a` and `b` point the same way, so they tie and `a` comes first.
`c` is a zero vector and scores 0. Upserting `a` replaces its vector (now
orthogonal to the query) and its metadata; deleting an unknown id changes
nothing.

**Example 3**

```
Input
["VectorStore", "upsert", "upsert", "query", "delete", "query", "query", "size"]
[[3], ["p", [1.0, 0.0, 0.0], {"lang": "go", "v": 2}], ["q", [0.0, 1.0, 0.0], {"lang": "go"}],
 [[1.0, 1.0, 0.0], 3, {"lang": "go", "v": 2}], ["p"], [[1.0, 1.0, 0.0], 3, {"lang": "go", "v": 2}],
 [[0.0, 0.0, 0.0], 3, {"lang": "go"}], []]

Output
[null, null, null, [["p", 0.7071067811865475, {"lang": "go", "v": 2}]], null, [], [["q", 0.0, {"lang": "go"}]], 1]
```

Explanation: `q` has no `"v"` key, so it does not match a filter that asks for
`"v": 2`. After `p` is deleted nothing matches. A zero query scores every
record 0.
