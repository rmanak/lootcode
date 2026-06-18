A binary tree is given as a LeetCode **level-order array** (`null`/`None` marks a
missing child) and rebuilt inside your function. The root is at column `0`, row `0`;
a left child is at `(col-1, row+1)` and a right child at `(col+1, row+1)`.

Return the vertical order traversal: process columns from left to right; within a
column list nodes from the top row down; nodes sharing the same `(col, row)` are
ordered by **increasing value**.

**Examples**
```
root = [3,9,20,null,null,15,7]   ->  [[9],[3,15],[20],[7]]
root = [1,2,3,4,5,6,7]           ->  [[4],[2],[1,5,6],[3],[7]]
```

**Constraints:** `1 <= number of nodes <= 1000`, `0 <= node value <= 1000`.
