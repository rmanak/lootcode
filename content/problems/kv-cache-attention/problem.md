When a transformer generates text one token at a time, each new token
**attends** to the tokens before it. Recomputing every earlier token's key and
value vectors at each step would waste work, so inference engines keep them in a
**KV cache**: each step appends one `(key, value)` pair, then attends over the
cache with its query. Many models also bound the cache's memory with
**sliding-window attention**: only the most recent `maxLen` entries are kept.

Implement the `KVCache` class:

- `KVCache(dim, maxLen)`: an empty cache for vectors of length `dim` that holds
  at most `maxLen` entries.
- `append(key, value)`: add one entry. If the cache already holds `maxLen`
  entries, first drop the **oldest** one.
- `attend(query)`: return the attention output over the entries currently in
  the cache, a list of `dim` numbers (defined below).
- `size()`: return the number of entries currently in the cache.

The attention output is a softmax-weighted average of the values, weighted by
how well each key matches the query. With $q$ the query, $k_i$ and $v_i$ the
key and value of cache entry $i$, and $d$ = `dim`:

$$
\begin{aligned}
s_i &= \frac{q \cdot k_i}{\sqrt{d}} \\
w_i &= \frac{e^{s_i}}{\sum_j e^{s_j}} \\
\text{output} &= \sum_i w_i\, v_i
\end{aligned}
$$

There is one score $s_i$ per entry in the cache, and the softmax runs over the
entries.

You may use **numpy** and the Python standard library. Inputs arrive as plain
lists. Numpy arrays are fine as return values.

**Numerical stability matters.** Keys and queries in the tests reach $\pm 100$,
so a score can reach tens of thousands, far past the point (about 709) where
`exp` overflows a float.

Every number `attend` returns is accepted when it is within a relative `1e-6`
(or an absolute `1e-9`) of the expected value. `size` must match exactly.

## Constraints

- `1 <= dim <= 16`
- `1 <= maxLen <= 1000`
- Every `key`, `value` and `query` has exactly `dim` numbers, each finite with
  absolute value `<= 100`
- `attend` is only called when the cache holds at least one entry
- At most `500` calls to `append`, `attend` and `size` in total

## Examples

**Example 1**

```
Input
["KVCache", "append", "append", "attend", "size"]
[[2, 4], [[1.0, 0.0], [1.0, 2.0]], [[0.0, 1.0], [3.0, 4.0]], [[2.0, 0.0]], []]

Output
[null, null, null, [1.3911406349860864, 2.3911406349860864], 2]
```

Explanation: the scores are `2/√2 ≈ 1.414` for the first key and `0` for the
second, so the weights are about `0.804` and `0.196`, and the output is
`0.804·[1, 2] + 0.196·[3, 4]`.

**Example 2**

```
Input
["KVCache", "append", "append", "append", "attend", "append", "attend", "size"]
[[1, 2], [[1.0], [10.0]], [[2.0], [20.0]], [[3.0], [30.0]], [[1.0]],
 [[4.0], [40.0]], [[1.0]], []]

Output
[null, null, null, null, [27.31058578630005], null, [37.31058578630005], 2]
```

Explanation: the window holds 2 entries, so the third append drops the first.
The first `attend` sees keys `2` and `3` (weights about `0.269` and `0.731`) and
returns `0.269·20 + 0.731·30 ≈ 27.31`. The fourth append drops key `2`, so the
second `attend` sees keys `3` and `4` and returns about `37.31`.

**Example 3**

```
Input
["KVCache", "append", "append", "append", "attend", "append", "attend", "size"]
[[2, 3], [[1.0, 1.0], [3.0, 0.0]], [[-1.0, 2.0], [0.0, 3.0]],
 [[4.0, -2.0], [6.0, 6.0]], [[0.0, 0.0]], [[0.0, 0.0], [9.0, 0.0]],
 [[0.0, 0.0]], []]

Output
[null, null, null, null, [3.0, 3.0], null, [5.0, 3.0], 3]
```

Explanation: a zero query scores every entry `0`, so attention is the plain
average of the values: `[3, 3]` for the first three. The fourth append drops
the oldest entry (value `[3, 0]`), leaving the average of `[0, 3]`, `[6, 6]`
and `[9, 0]`, which is `[5, 3]`.
