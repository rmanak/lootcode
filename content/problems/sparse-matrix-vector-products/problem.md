Large linear models (a ranking model's weight matrix over millions of
features, a graph's adjacency matrix) are stored as **sparse matrices**: only
the non-zero entries are kept. Implement one that can be updated and
multiplied by a sparse vector **from either side**.

- `SparseMatrix(rows, cols, entries)` creates a `rows x cols` matrix whose
  non-zero entries are given as `[i, j, value]` triples (row $i$, column $j$);
  every other entry is $0$.
- `set(i, j, value)` sets entry $(i, j)$ to `value`, which may be $0$.
- `multiplyVector(vector)` returns $M v$, for a column vector $v$ of length
  `cols`.
- `vectorMultiply(vector)` returns $v^\top M$, for a row vector $v$ of length
  `rows`.

Vectors, given and returned, are sparse too: a list of `[index, value]` pairs
with strictly increasing indices, listing exactly the non-zero entries. A
result entry that cancels to $0$ is left out.

The dimensions can be as large as $10^9$, so nothing may be proportional to
`rows` or `cols`. Each product should cost time proportional to the number of
matrix entries it actually multiplies (plus sorting the result), and `set`
should be fast.

## Constraints

- `1 <= rows, cols <= 10⁹`; at most `10⁵` initial entries, at distinct positions,
  with non-zero values
- All values (matrix and vector) are integers in `[-10⁴, 10⁴]`; vector values are non-zero
- A vector has at most `10⁴` pairs, with indices strictly increasing and in range
- At most `5000` calls in total

## Examples

**Example 1**

```
Input
["SparseMatrix", "multiplyVector", "vectorMultiply"]
[[2, 3, [[0, 1, 3], [1, 1, 4], [1, 2, 5]]], [[[1, 2], [2, 3]]], [[[0, 1], [1, -1]]]]

Output
[null, [[0, 6], [1, 23]], [[1, -1], [2, -5]]]
```

Explanation: the matrix is [[0, 3, 0], [0, 4, 5]]. With v = [0, 2, 3],
M·v = [6, 8 + 15]. With v = [1, −1], vᵀ·M = row 0 − row 1 = [0, −1, −5], and
the 0 is left out.

**Example 2**

```
Input
["SparseMatrix", "multiplyVector", "set", "set", "multiplyVector"]
[[3, 3, [[0, 0, 1], [2, 0, -2], [2, 2, 1]]], [[[0, 2], [2, 4]]], [2, 0, 0], [1, 2, 7], [[[0, 2], [2, 4]]]]

Output
[null, [[0, 2]], null, null, [[0, 2], [1, 28], [2, 4]]]
```

Explanation: row 2 of the first product is −2·2 + 1·4 = 0, so it is left out.
Setting (2, 0) to 0 removes that entry.

**Example 3**

```
Input
["SparseMatrix", "vectorMultiply", "set", "multiplyVector"]
[[1000000000, 1000000000, [[999999999, 5, 2], [7, 999999999, -1]]], [[[7, 3], [999999999, 1]]], [999999999, 5, 9],
 [[[5, 1], [6, 8]]]]

Output
[null, [[5, 2], [999999999, -3]], null, [[999999999, 9]]]
```

Explanation: the matrix is a billion by a billion with two non-zero entries.
Column 6 of the vector meets no stored entry.
