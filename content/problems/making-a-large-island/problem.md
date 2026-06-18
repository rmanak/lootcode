You are given an `n x n` binary `grid`. You may change **at most one** `0` to a `1`.
Return the size of the largest island (a 4-directionally connected group of `1`s) you
can obtain afterward. If the grid is all `1`s, no change is made.

**Examples**
```
grid = [[1,0],[0,1]]   ->  3   (flip one 0 to join the two 1s)
grid = [[1,1],[1,0]]   ->  4   (flip the 0)
grid = [[1,1],[1,1]]   ->  4   (already one island)
```

**Constraints:** `1 <= n <= 50`, `grid[i][j]` is `0` or `1`.
