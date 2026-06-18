Given an `m x n` matrix `mat` and an integer `threshold`, **return the maximum
side-length of a square sub-matrix whose sum is `<= threshold`** (or `0` if no such
square exists).

**Examples**
```
mat = [[1,1,3,2,4,3,2],[1,1,3,2,4,3,2],[1,1,3,2,4,3,2]], threshold = 4  ->  2
mat = [[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2],[2,2,2,2,2]], threshold = 1  ->  0
mat = [[1,1,1,1],[1,0,0,0],[1,0,0,0],[1,0,0,0]], threshold = 6        ->  3
```

**Constraints:** `1 <= m, n <= 300`, `0 <= mat[i][j] <= 10^4`,
`0 <= threshold <= 10^5`.
