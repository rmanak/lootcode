A binary tree with distinct node values is given as a LeetCode **level-order array**
(`null`/`None` marks a missing child) and rebuilt inside your function. After deleting
every node whose value is in `to_delete`, the tree breaks into a forest. Return the
roots of the remaining trees, each serialized as a level-order array (`None` for a
missing child, trailing `None`s trimmed). The trees may be returned in **any order**.

**Example**
```
root = [1,2,3,4,5,6,7], to_delete = [3,5]   ->  [[1,2,null,4],[6],[7]]
```

**Constraints:** `1 <= number of nodes <= 1000`, distinct values in `1..1000`.
