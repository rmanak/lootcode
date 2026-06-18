In a gold-mine `grid`, each cell holds an amount of gold (`0` means empty). Starting
from any non-empty cell, you repeatedly walk one step up/down/left/right into a cell
that still has gold, collecting all the gold in each cell you enter. You may not revisit
a cell and may not step onto a `0` cell. Return the maximum gold you can collect.

**Examples**
```
grid = [[0,6,0],[5,8,7],[0,9,0]]                 ->  24   (9 -> 8 -> 7)
grid = [[1,0,7],[2,0,6],[3,4,5],[0,3,0],[9,0,20]]   ->  28   (1->2->3->4->5->6->7)
```

**Constraints:** `1 <= rows, cols <= 15`, `0 <= grid[i][j] <= 100`, at most 25 gold cells.
