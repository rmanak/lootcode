A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Levels are numbered from `1` at the
root. Return the **smallest** level whose node values sum to the maximum.

**Examples**
```
root = [1,7,0,7,-8,null,null]   ->  2   (level 2 sum = 7 is maximal)
```

**Constraints:** `1 <= number of nodes <= 10^4`, `-10^5 <= node value <= 10^5`.
