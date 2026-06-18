A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return the maximum value `|a - b|`
over all pairs of nodes where one is an **ancestor** of the other.

**Examples**
```
root = [8,3,10,1,6,null,14,null,null,4,7,13]   ->  7   (|8 - 1| = 7)
root = [1,null,2,null,0,3]                      ->  3
```

**Constraints:** `2 <= number of nodes <= 5000`, `0 <= node value <= 10^5`.
