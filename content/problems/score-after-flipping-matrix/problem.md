Given a binary matrix `grid`, a move toggles every value in a chosen row or column
(`0 <-> 1`). After any number of moves, each row is read as a binary number; the
matrix score is the sum of those numbers. Return the highest achievable score.

**Example**
```
grid = [[0,0,1,1],[1,0,1,0],[1,1,0,0]]  ->  39
    (toggle to [[1,1,1,1],[1,0,0,1],[1,1,1,1]] -> 15 + 9 + 15 = 39)
```

**Constraints:** `1 <= m, n <= 20`, every `grid[i][j]` is `0` or `1`.
