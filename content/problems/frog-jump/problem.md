A frog crosses a river on stones at the given sorted positions, starting on the first
stone with a mandatory first jump of `1`. If the last jump was `k`, the next must be
`k-1`, `k`, or `k+1` (forward only) and must land on a stone. **Return `true` if the
frog can reach the last stone.**

**Examples**
```
stones = [0,1,3,5,6,8,12,17]  ->  true
stones = [0,1,2,3,4,8,9,11]   ->  false
```

**Constraints:** `2 <= len(stones) <= 2000`, first stone is `0`, strictly increasing.
