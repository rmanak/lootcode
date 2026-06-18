A brick wall has several rows; `wall[i]` lists the widths of the bricks in row `i`
from left to right. All rows have the **same total width**. Draw one vertical line
from top to bottom; a brick is *crossed* unless the line passes exactly along one
of its edges. The line may not run along the two outer edges of the wall.

Return the **least number of bricks** the line must cross.

**Example**
```
wall = [[1,2,2,1],
        [3,1,2],
        [1,3,2],
        [2,4],
        [3,1,2],
        [1,3,1,1]]   ->  2
```

**Constraints:** `1 <= len(wall) <= 10^4`, each row has `1..10^4` bricks, total
bricks `<= 2*10^4`, row widths are equal.
