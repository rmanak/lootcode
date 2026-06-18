A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The width of a level is the distance
between its leftmost and rightmost non-null nodes, counting the (possibly null)
positions a full binary tree would place between them. Return the maximum width over
all levels.

**Examples**
```
root = [1,3,2,5,3,null,9]                       ->  4
root = [1,3,2,5,null,null,9,6,null,null,7]      ->  8
```

**Constraints:** `1 <= number of nodes <= 3000`; the answer fits in a 32-bit integer.
