In one step you pick a cell and flip it **and its (up to four) edge-adjacent
neighbours** (flip toggles `0`/`1`). **Return the minimum number of steps to make
`mat` all zeros, or `-1` if impossible.**

**Examples**
```
mat = [[0,0],[0,1]]           ->  3
mat = [[0]]                   ->  0
mat = [[1,1,1],[1,0,1],[0,0,0]]  ->  6
mat = [[1,0,0],[1,0,0]]       ->  -1
```

**Constraints:** `1 <= m, n <= 3`, `mat[i][j]` in `{0, 1}`.
