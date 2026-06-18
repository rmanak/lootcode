A move takes a point `(x, y)` to either `(x, x + y)` or `(x + y, y)`. Given a start
`(sx, sy)` and a target `(tx, ty)`, return `true` if some sequence of moves
transforms the start into the target, and `false` otherwise.

**Examples**
```
sx=1, sy=1, tx=3, ty=5  ->  true   ((1,1)->(1,2)->(3,2)->(3,5))
sx=1, sy=1, tx=2, ty=2  ->  false
sx=1, sy=1, tx=1, ty=1  ->  true
```

**Constraints:** `1 <= sx, sy, tx, ty <= 10^9`.
