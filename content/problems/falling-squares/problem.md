Squares are dropped onto a number line one at a time. The `i`-th drop
`positions[i] = [left, side]` places a square whose left edge is at `left` with side
length `side`. Each square falls from above and sticks the moment it lands on the
number line or on top of any square it overlaps (sharing only a corner does **not**
count). After each drop, record the current tallest stack height. Return the list of
these heights.

**Example**
```
positions = [[1,2],[2,3],[6,1]]   ->  [2,5,5]
```

**Constraints:** `1 <= len(positions) <= 1000`, `1 <= left, side <= 10^8`.
