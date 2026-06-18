You are given a `matrix` of `0`s and `1`s. You may choose any set of columns and flip
every cell in each chosen column (`0 <-> 1`). Return the maximum number of rows that
can be made **all equal** (every cell in the row identical) after some choice of flips.

**Examples**
```
[[0,1],[1,1]]            ->  1
[[0,1],[1,0]]            ->  2
[[0,0,0],[0,0,1],[1,1,0]]   ->  2
```

**Constraints:** `1 <= rows, cols <= 300`, `matrix[i][j]` is `0` or `1`.
