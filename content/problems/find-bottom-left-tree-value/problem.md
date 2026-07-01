> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Return the leftmost value in the
**last** (deepest) row of the tree.

**Examples**
```
root = [2,1,3]                          ->  1
root = [1,2,3,4,null,5,6,null,null,7]   ->  7
```

**Constraints:** `1 <= number of nodes <= 10^4`.
