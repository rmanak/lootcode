Given an `m x n` matrix `mat` and an integer `k`, return a matrix `answer` where
`answer[i][j]` is the sum of every `mat[r][c]` with `i - k <= r <= i + k`,
`j - k <= c <= j + k`, and `(r, c)` a valid cell of `mat`.

**Examples**
```
mat = [[1,2,3],[4,5,6],[7,8,9]], k = 1  ->  [[12,21,16],[27,45,33],[24,39,28]]
mat = [[1,2,3],[4,5,6],[7,8,9]], k = 2  ->  [[45,45,45],[45,45,45],[45,45,45]]
```

**Constraints:** `1 <= m, n, k <= 100`, `1 <= mat[i][j] <= 100`.
