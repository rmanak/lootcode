`heights[i]` is the terrain height at index `i` (each column has width 1). Drop `V`
units of water one at a time at index `K`. Each unit settles by the rule: if it can
eventually fall lower by moving left, it moves left to the lowest such position;
otherwise if it can eventually fall lower by moving right, it goes right; otherwise it
rests at `K`. "Level" means terrain height plus any water already there. Return the
final heights (terrain + water) at each index.

**Examples**
```
heights = [2,1,1,2,1,2,2], V = 4, K = 3   ->  [2,2,2,3,2,2,2]
heights = [1,2,3,4], V = 2, K = 2          ->  [2,3,3,4]
heights = [3,1,3], V = 5, K = 1            ->  [4,4,4]
```

**Constraints:** `1 <= len(heights) <= 100`, `0 <= heights[i] <= 99`,
`0 <= V <= 2000`, `0 <= K < len(heights)`.
