> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). Return a list whose `i`-th entry
is the largest value found in the `i`-th row (level) of the tree, top to bottom. An
empty tree returns an empty list.

**Example**
```
root = [1,3,2,5,3,null,9]   ->  [1,3,9]
```

**Constraints:** `0 <= number of nodes <= 10^4`, node values fit in a 32-bit
integer.
