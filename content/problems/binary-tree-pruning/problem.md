> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree with values `0`/`1` is given as a `TreeNode`
(`null`/`None` marks a missing child). Remove every
subtree that does not contain a `1` (i.e. a subtree whose nodes are all `0`).

Return the root of the pruned tree (a `TreeNode`), or `None` if the whole tree is
removed.

**Examples**
```
root = [1,null,0,0,1]   ->  [1,null,0,null,1]
root = [0]              ->  []
root = [1]              ->  [1]
```

**Constraints:** `1 <= number of nodes <= 200`, each value is `0` or `1`.
