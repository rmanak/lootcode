`grid[i][j] == 1` marks a server. Two servers communicate if they share a row or a
column. **Return the number of servers that communicate with at least one other server.**

**Examples**
```
[[1,0],[0,1]]  ->  0
[[1,0],[1,1]]  ->  3
```

**Constraints:** `1 <= m, n <= 250`, `grid[i][j]` is `0` or `1`.
