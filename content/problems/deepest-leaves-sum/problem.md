> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Return the sum of the values of the
deepest leaves (the nodes at maximum depth).

**Example**
```
root = [1,2,3,4,5,null,6,7,null,null,null,null,8]   ->  15
```

**Constraints:** `1 <= number of nodes <= 10^4`, `1 <= value <= 100`.
