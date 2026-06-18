You are given two lists of closed intervals, `A` and `B`. Each list is pairwise
disjoint and sorted by start. Return the intersection of the two lists: every closed
interval `[lo, hi]` (with `lo <= hi`) common to one interval of `A` and one of `B`,
in sorted order.

**Example**
```
A = [[0,2],[5,10],[13,23],[24,25]]
B = [[1,5],[8,12],[15,24],[25,26]]
   ->  [[1,2],[5,5],[8,10],[15,23],[24,24],[25,25]]
```

**Constraints:** `0 <= len(A), len(B) < 1000`, `0 <= endpoints < 10^9`.
