> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). A *zigzag path* starts at any
node and a chosen direction, alternates left/right at each step, and stops when it
cannot move. Its length is the number of nodes visited minus one (a single node has
length `0`). Return the longest zigzag path length in the tree.

**Examples**
```
root = [1]              ->  0
root = [1,2,3]          ->  1
root = [1,2,null,null,3] -> 2   (1 -> left 2 -> right 3)
```

**Constraints:** `1 <= number of nodes <= 5*10^4`.
