Given non-negative `A`, pick two **non-overlapping** contiguous subarrays of lengths
`L` and `M` (in either relative order) to **maximize their combined sum.** Return
that maximum.

**Examples**
```
A = [0,6,5,2,2,5,1,9,4], L = 1, M = 2     ->  20
A = [3,8,1,3,2,1,8,9,0], L = 3, M = 2     ->  29
A = [2,1,5,6,0,9,5,0,3,8], L = 4, M = 3   ->  31
```

**Constraints:** `1 <= L, M`, `L + M <= len(A) <= 1000`, `0 <= A[i] <= 1000`.
