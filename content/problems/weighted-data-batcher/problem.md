Training a language model mixes several datasets (web text, code, books) in
fixed proportions, and a long run is paused and resumed many times. Resuming
must reproduce **exactly** the batches the run would have seen, without
replaying the data. Implement the batcher.

- `DataBatcher(names, weights, batchSize)`: dataset `names[d]` should make up
  a share `weights[d] / sum(weights)` of the examples. Every dataset is an
  endless stream, and its $k$-th example (counting from $0$) is the string
  `"<name>:<k>"`, so `"code:3"` is the fourth example of `code`. Reading the
  next example of a dataset just increments its **offset**.
- `nextBatch()` returns the next `batchSize` examples.
- `stateDict()` returns everything needed to resume, as `[offsets, current]`
  (defined below).
- `loadStateDict(state)` restores a state returned by an earlier `stateDict()`;
  from then on, batches continue exactly as they did after that call.

**Which dataset fills each slot** is decided by **smooth weighted
round-robin**, the scheme nginx uses to spread requests over weighted servers.
It keeps a `current` score per dataset, all $0$ at the start. For every slot of
every batch, one after another:

1. add each dataset's weight to its `current` score;
2. pick the dataset with the highest `current` score (on a tie, the one that
   comes first in `names`) and take its next example;
3. subtract `sum(weights)` from the picked dataset's `current` score.

Over any `sum(weights)` consecutive slots each dataset is picked exactly
`weights[d]` times, interleaved as evenly as possible, and because the scores
carry over from one batch to the next, the proportions hold even when
`batchSize` is not a multiple of `sum(weights)`.

`offsets[d]` is how many examples dataset $d$ has given out so far, and
`current[d]` its current score.

## Constraints

- `1 <= len(names) <= 10`; names are distinct, non-empty, at most `20`
  characters of letters, digits, `_` and `-`
- Every weight is an integer in `[1, 100]`; `1 <= batchSize <= 256`
- `loadStateDict` is only given states that `stateDict` returned earlier
- At most `500` calls in total

## Examples

**Example 1**

```
Input
["DataBatcher", "nextBatch", "nextBatch"]
[[["web", "code"], [2, 1], 6], [], []]

Output
[null, ["web:0", "code:0", "web:1", "web:2", "code:1", "web:3"],
 ["web:4", "code:2", "web:5", "web:6", "code:3", "web:7"]]
```

Explanation: the scores after adding the weights go [2, 1] → pick web
([-1, 1]); [1, 2] → pick code ([1, -1]); [3, 0] → pick web ([0, 0]), and the
pattern web, code, web repeats every 3 slots.

**Example 2**

```
Input
["DataBatcher", "nextBatch", "stateDict", "nextBatch", "nextBatch", "loadStateDict", "nextBatch"]
[[["a", "b", "c"], [5, 1, 1], 4], [], [], [], [], [[[3, 1, 0], [-1, -3, 4]]], []]

Output
[null, ["a:0", "a:1", "b:0", "a:2"], [[3, 1, 0], [-1, -3, 4]], ["c:0", "a:3", "a:4", "a:5"],
 ["a:6", "b:1", "a:7", "c:1"], null, ["c:0", "a:3", "a:4", "a:5"]]
```

Explanation: in the third slot b and c tie at 3, and b comes first in
`names`. Loading the saved state rewinds both the offsets and the scores, so
the next batch is the second batch again.

**Example 3**

```
Input
["DataBatcher", "nextBatch", "stateDict", "nextBatch"]
[[["x", "y"], [1, 1], 3], [], [], []]

Output
[null, ["x:0", "y:0", "x:1"], [[2, 1], [-1, 1]], ["y:1", "x:2", "y:2"]]
```

Explanation: the scores carry over between batches, so the second batch
starts with y rather than restarting at x.
