> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Houses form a binary tree, given as a `TreeNode` (`null`/`None`
marks a missing child). The alarm triggers if two
**directly-linked** houses (a parent and its child) are both robbed. Return the
maximum total amount that can be robbed without alerting the police.

**Examples**
```
root = [3,2,3,null,3,null,1]   ->  7   (3 + 3 + 1)
root = [3,4,5,1,3,null,1]      ->  9   (4 + 5)
```

**Constraints:** `1 <= number of nodes <= 10^4`, `0 <= node value <= 10^4`.
