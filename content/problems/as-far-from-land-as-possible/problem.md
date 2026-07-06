In a grid of `0` (water) and `1` (land), **return the largest Manhattan distance from
a water cell to its nearest land cell**, or `-1` if the grid is all water or all
land.

**Examples**
```
grid = [[1,0,1],[0,0,0],[1,0,1]]  ->  2
grid = [[1,0,0],[0,0,0],[0,0,0]]  ->  4
```

**Constraints:** the grid is rectangular with `1 <= len(grid) <= 100` rows and `1 <= len(grid[0]) <= 100` columns (all rows the same length); cells are `0`/`1`.
