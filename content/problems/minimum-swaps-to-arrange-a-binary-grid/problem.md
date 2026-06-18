You may swap two **adjacent rows** of an `n x n` binary grid in one step. The grid is
*valid* when every cell above the main diagonal is `0`. **Return the minimum number of
swaps to make it valid, or `-1` if impossible.**

**Examples**
```
grid = [[0,0,1],[1,1,0],[1,0,0]]  ->  3
grid = [[0,1,1,0],[0,1,1,0],[0,1,1,0],[0,1,1,0]]  ->  -1
grid = [[1,0,0],[1,1,0],[1,1,1]]  ->  0
```

**Constraints:** `1 <= n <= 200`, `grid[i][j]` is `0` or `1`.
