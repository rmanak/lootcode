In an `n x n` grid (`0` = empty, `1` = blocked), a snake occupies two cells and
starts horizontally at `(0,0)` and `(0,1)`. Each move it may:

- move right one cell (if the destination cells are empty),
- move down one cell (if the destination cells are empty),
- rotate **clockwise** from horizontal to vertical when the two cells directly below
  it are both empty: `(r,c),(r,c+1)` -> `(r,c),(r+1,c)`,
- rotate **counter-clockwise** from vertical to horizontal when the two cells
  directly to its right are both empty: `(r,c),(r+1,c)` -> `(r,c),(r,c+1)`.

Return the minimum number of moves so the snake reaches `(n-1,n-2)` and `(n-1,n-1)`,
or `-1` if impossible.

**Example**
```
grid = [[0,0,0,0,0,1],[1,1,0,0,1,0],[0,0,0,0,1,1],
        [0,0,1,0,1,0],[0,1,1,0,0,0],[0,1,1,0,0,0]]   ->  11
```

**Constraints:** `2 <= n <= 100`; the snake starts on empty cells.
