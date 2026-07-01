> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). The root is at depth `1`. Insert a
new row of nodes all holding value `v` at depth `d`: for every node `N` at depth
`d-1`, `N`'s original left subtree becomes the left subtree of a new left child
(value `v`), and `N`'s original right subtree becomes the right subtree of a new right
child (value `v`). If `d == 1`, a new root with value `v` is created whose left child
is the original tree. Return the root of the new tree (a `TreeNode`).

**Examples**
```
root = [4,2,6,3,1,5], v = 1, d = 2   ->  [4,1,1,2,null,null,6,3,1,5]
root = [4,2,null,3,1], v = 1, d = 3  ->  [4,2,null,1,1,3,null,null,1]
```

**Constraints:** `1 <= number of nodes`; `1 <= d <= (tree depth) + 1`.
