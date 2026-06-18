Given the `preorder` traversal of a binary search tree (every value distinct), build
the BST and return it as a LeetCode **level-order array** (`None` for a missing child,
trailing `None`s trimmed). Recall a BST keeps `node.left < node < node.right`.

**Example**
```
preorder = [8,5,1,7,10,12]   ->  [8,5,10,1,7,null,12]
```

**Constraints:** `1 <= len(preorder) <= 100`, `1 <= preorder[i] <= 10^8`, distinct.
