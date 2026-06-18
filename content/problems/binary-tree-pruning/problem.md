A binary tree with values `0`/`1` is given as a LeetCode **level-order array**
(`null`/`None` marks a missing child) and rebuilt inside your function. Remove every
subtree that does not contain a `1` (i.e. a subtree whose nodes are all `0`).

Return the resulting tree as a level-order array (`None` for a missing child, with
trailing `None`s trimmed); return `[]` if the whole tree is removed.

**Examples**
```
root = [1,null,0,0,1]   ->  [1,null,0,null,1]
root = [0]              ->  []
root = [1]              ->  [1]
```

**Constraints:** `1 <= number of nodes <= 200`, each value is `0` or `1`.
