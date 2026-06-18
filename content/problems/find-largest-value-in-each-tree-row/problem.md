A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and is rebuilt inside your function. Return a list whose `i`-th entry
is the largest value found in the `i`-th row (level) of the tree, top to bottom. An
empty tree returns an empty list.

**Example**
```
root = [1,3,2,5,3,null,9]   ->  [1,3,9]
```

**Constraints:** `0 <= number of nodes <= 10^4`, node values fit in a 32-bit
integer.
