> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

A binary tree is given as a `TreeNode` (`null`/`None` marks a
missing child). The *subtree sum* of a node is the
sum of all values in the subtree rooted at that node. Return all subtree-sum values
that occur most frequently (in **any order**).

**Examples**
```
root = [5,2,-3]   ->  [2,-3,4]   (each sum occurs once)
root = [5,2,-5]   ->  [2]        (sum 2 occurs twice)
```

**Constraints:** `1 <= number of nodes <= 10^4`.
