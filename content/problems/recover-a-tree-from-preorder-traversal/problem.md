A preorder DFS prints, for each node, `D` dashes (where `D` is the node's depth, root
depth `0`) followed by the node's value. A node with a single child always has that
child on the **left**. Given the printed string `traversal`, rebuild the tree and
return its **level-order array** (`None` for a missing child, trailing `None`s
trimmed).

**Examples**
```
"1-2--3--4-5--6--7"      ->  [1,2,5,3,4,6,7]
"1-2--3---4-5--6---7"    ->  [1,2,5,3,null,6,null,4,null,7]
"1-401--349---90--88"    ->  [1,401,null,349,88,90]
```

**Constraints:** `1 <= number of nodes <= 1000`, `1 <= node value <= 10^9`.
