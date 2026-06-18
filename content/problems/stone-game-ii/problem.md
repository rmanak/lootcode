`piles[i]` is the number of stones in the `i`-th pile, arranged in a row. Alice and
Bob alternate turns, Alice first, with `M = 1` initially. On a turn the current
player takes **all** the stones in the first `X` remaining piles for some
`1 <= X <= 2M`, then `M` becomes `max(M, X)`. Play continues until no piles remain.
Both play optimally to maximise their own stones; return the maximum number of
stones Alice can collect.

**Example**
```
piles = [2,7,9,4,4]   ->  10
```

**Constraints:** `1 <= len(piles) <= 100`, `1 <= piles[i] <= 10^4`.
