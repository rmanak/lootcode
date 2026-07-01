> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A linked list is given as an array of values `head`, and a binary tree as a LeetCode
**level-order array** `root` (`null`/`None` for a missing child). Return `True` if the
values of `head` (starting from its first element) match the values along some
**downward path** in the tree (a path that goes from a node strictly toward its
descendants), otherwise `False`.

**Examples**
```
head = [4,2,8], root = [1,4,4,null,2,2,null,1,null,6,8]   ->  true
head = [1,4,2,6,8], root = [1,4,4,null,2,2,null,1,null,6,8]  ->  false
```

**Constraints:** `1 <= len(head) <= 100`; the tree has between 1 and 2500 nodes;
values are in `[1, 100]`.
