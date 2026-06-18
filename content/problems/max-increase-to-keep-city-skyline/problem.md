`grid[i][j]` is the height of a building. You may raise any buildings so that the
skyline seen from the top, bottom, left and right is unchanged. The top/bottom
skyline is the per-column maxima; the left/right skyline is the per-row maxima.
**Return the maximum total increase** in height.

A building at `(i, j)` may rise to `min(rowMax[i], colMax[j])` without changing any
skyline.

**Example**
```
grid = [[3,0,8,4],[2,4,5,7],[9,2,6,3],[0,3,1,0]]  ->  35
```

**Constraints:** `2 <= len(grid) == len(grid[0]) <= 50`, `0 <= grid[i][j] <= 100`.
