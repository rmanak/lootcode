> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Return all root-to-leaf paths whose
node values sum to `targetSum`. Each path lists node values from root to leaf; the
paths may be returned in **any order**.

**Example**
```
root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22
    ->  [[5,4,11,2],[5,8,4,5]]
```

**Constraints:** `0 <= number of nodes <= 5000`.
