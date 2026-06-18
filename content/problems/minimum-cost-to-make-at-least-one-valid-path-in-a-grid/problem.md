Each cell holds an arrow: `1` right, `2` left, `3` down, `4` up. Starting at `(0,0)`
you follow arrows; you want to reach `(m-1, n-1)`. Changing one cell's arrow costs
`1` (each cell at most once). **Return the minimum total cost to create at least one
valid path** from top-left to bottom-right.

**Examples**
```
grid = [[1,1,1,1],[2,2,2,2],[1,1,1,1],[2,2,2,2]]  ->  3
grid = [[1,1,3],[3,2,2],[1,1,4]]                  ->  0
grid = [[1,2],[4,3]]                              ->  1
```

**Constraints:** `1 <= m, n <= 100`, `grid[i][j]` in `{1,2,3,4}`.
