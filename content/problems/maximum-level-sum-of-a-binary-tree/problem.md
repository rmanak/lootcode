> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Levels are numbered from `1` at the
root. Return the **smallest** level whose node values sum to the maximum.

**Examples**
```
root = [1,7,0,7,-8,null,null]   ->  2   (level 2 sum = 7 is maximal)
```

**Constraints:** `1 <= number of nodes <= 10^4`, `-10^5 <= node value <= 10^5`.
