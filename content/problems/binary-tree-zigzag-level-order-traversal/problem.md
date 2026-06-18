A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. Return its *zigzag* level-order
traversal: read the first level left-to-right, the next right-to-left, and keep
alternating.

**Example**
```
root = [3,9,20,null,null,15,7]   ->  [[3],[20,9],[15,7]]
```

**Constraints:** `0 <= number of nodes <= 2000`.
