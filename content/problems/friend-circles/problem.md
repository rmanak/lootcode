There are `n` students. `M` is an `n x n` matrix where `M[i][j] == 1` means students
`i` and `j` are direct friends (`M` is symmetric with `1`s on the diagonal).
Friendship is transitive: a *friend circle* is a maximal group of directly or
indirectly connected students. Return the number of friend circles.

**Examples**
```
M = [[1,1,0],[1,1,0],[0,0,1]]   ->  2
M = [[1,0,0],[0,1,0],[0,0,1]]   ->  3
```

**Constraints:** `1 <= n <= 200`, `M[i][j]` is `0` or `1`, `M[i][i] == 1`,
`M[i][j] == M[j][i]`.
