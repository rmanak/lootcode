Given two **sparse** matrices `mat1` of size `m x k` and `mat2` of size
`k x n`, return their product `mat1 × mat2`.

Entry `(i, j)` of the product is $\sum_{t} \texttt{mat1}[i][t] \cdot \texttt{mat2}[t][j]$.
Most entries of both matrices are zero (embedding lookups and bag-of-words
features produce matrices like these), so an algorithm that does work only for
the non-zero entries is far faster than the dense triple loop.

## Constraints

- `1 <= m, k, n <= 300`; `mat1` is `m x k` and `mat2` is `k x n`
- `-100 <= mat1[i][j], mat2[i][j] <= 100`

## Examples

**Example 1**
```
Input:  mat1 = [[1, 0, 0], [-1, 0, 3]], mat2 = [[7, 0, 0], [0, 0, 0], [0, 0, 1]]
Output: [[7, 0, 0], [-7, 0, 3]]
```

**Example 2**
```
Input:  mat1 = [[0]], mat2 = [[0]]
Output: [[0]]
```

**Example 3**
```
Input:  mat1 = [[0, 2, 0], [0, -3, 4]], mat2 = [[5, 1], [0, 6], [2, 0]]
Output: [[0, 12], [8, -18]]
Explanation: row 1 of the product is −3 · [0, 6] + 4 · [2, 0] = [8, −18].
```
