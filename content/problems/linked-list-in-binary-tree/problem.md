You are given a **singly linked list** `head` (each node a `ListNode` with `.val`
and `.next`) and the `root` of a **binary tree** (each node a `TreeNode` with
`value`, `left`, `right`). Both classes are provided.

Return `True` if the values of `head`, starting from its first node, match the
values along some **downward path** in the tree (a path that goes from a node
strictly toward its descendants, always continuing to a child), otherwise `False`.

> **Format:** the linked list is shown below as the array of its node values, and
the tree in LeetCode **level-order array** form (`null` = missing child; trailing
`null`s dropped).

**Examples**
```
head = [4,2,8], root = [1,4,4,null,2,2,null,1,null,6,8]      ->  true
head = [1,4,2,6,8], root = [1,4,4,null,2,2,null,1,null,6,8]  ->  false
```

**Constraints:** `1 <= number of list nodes <= 100`; the tree has between 1 and 2500
nodes; values are in `[1, 100]`.
