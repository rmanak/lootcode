You have stones with positive integer weights. Repeatedly pick two stones of
weights `x <= y` and smash them: if `x == y` both are destroyed, otherwise the one
of weight `x` is destroyed and the other becomes `y - x`. At most one stone
remains. Return the smallest possible weight of that stone (`0` if none remain).

**Example**
```
stones = [2,7,4,1,8,1]   ->  1
```

**Constraints:** `1 <= len(stones) <= 30`, `1 <= stones[i] <= 100`.
