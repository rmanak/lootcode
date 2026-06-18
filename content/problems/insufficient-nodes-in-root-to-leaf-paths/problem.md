A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. A node is *insufficient* if every
root-to-leaf path passing through it has sum **strictly less than** `limit`. Delete
all insufficient nodes simultaneously and return the resulting tree as a level-order
array (`None` for a missing child, trailing `None`s trimmed); return `[]` if the whole
tree is deleted.

**Examples**
```
root = [1,2,3,4,-99,-99,7,8,9,-99,-99,12,13,-99,14], limit = 1
    ->  [1,2,3,4,null,null,7,8,9,null,14]
root = [1,2,-3,-5,null,4,null], limit = -1   ->  [1,null,-3,4]
```

**Constraints:** `1 <= number of nodes <= 5000`, `-10^5 <= value <= 10^5`.
