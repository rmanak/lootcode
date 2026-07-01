> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Return its *zigzag* level-order
traversal: read the first level left-to-right, the next right-to-left, and keep
alternating.

**Example**
```
root = [3,9,20,null,null,15,7]   ->  [[3],[20,9],[15,7]]
```

**Constraints:** `0 <= number of nodes <= 2000`.
