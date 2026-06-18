A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. All node values are distinct.

The depth of the root is `0`. The *deepest leaves* are the leaves at the maximum
depth in the tree. Return the **value** of the lowest common ancestor (the deepest
node that has all of the deepest leaves in its subtree) of those deepest leaves.

**Examples**
```
root = [1,2,3]          ->  1   (deepest leaves 2 and 3; their LCA is the root)
root = [1,2,3,4]        ->  4   (the single deepest leaf is its own ancestor)
root = [1,2,3,4,5]      ->  2   (deepest leaves 4 and 5; their LCA is node 2)
```

**Constraints:** `1 <= number of nodes <= 1000`, node values are distinct.
