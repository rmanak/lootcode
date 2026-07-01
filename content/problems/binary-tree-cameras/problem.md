> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). A camera placed on a node monitors its
parent, itself, and its immediate children. Return the minimum number of cameras needed
so that **every** node is monitored.

**Examples**
```
root = [0,0,null,0,0]              ->  1
root = [0,0,null,0,null,0,null,null,0]  ->  2
```

**Constraints:** `1 <= number of nodes <= 1000`; every node value is `0`.
