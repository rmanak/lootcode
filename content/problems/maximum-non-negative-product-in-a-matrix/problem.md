From the top-left to the bottom-right of `grid`, moving only right or down, **return
the maximum non-negative product** of the visited cells, modulo `10^9 + 7`. If every
path has a negative product, return `-1`. (The modulo is applied after taking the
maximum.)

**Examples**
```
grid = [[1,-2,1],[1,-2,1],[3,-4,1]]  ->  8
grid = [[1,3],[0,-4]]                ->  0
grid = [[-1,-2,-3],[-2,-3,-3],[-3,-3,-2]]  ->  -1
```

**Constraints:** `1 <= rows, cols <= 15`, `-4 <= grid[i][j] <= 4`.
