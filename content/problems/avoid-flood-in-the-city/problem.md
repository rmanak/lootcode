There are infinitely many lakes, all initially empty. You are given an array
`rains`:

- `rains[i] > 0`: it rains on lake `rains[i]`, filling it. If that lake is already
  full, a flood occurs.
- `rains[i] == 0`: a dry day — you may dry exactly one (any) currently-full lake,
  emptying it.

Return `true` if it is possible to choose the dry-day actions so that **no flood
ever happens**, and `false` otherwise.

**Examples**
```
rains = [1,2,3,4]      ->  true
rains = [1,2,0,0,2,1]  ->  true
rains = [1,2,0,1,2]    ->  false
rains = [10,20,20]     ->  false
```

**Constraints:** `1 <= len(rains) <= 10^5`, `0 <= rains[i] <= 10^9`.
