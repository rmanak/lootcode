A **ramp** is a pair of indices `(i, j)` with `i < j` and `A[i] <= A[j]`; its width
is `j - i`. Return the maximum width over all ramps in `A`, or `0` if none exists.

**Examples**
```
A = [6,0,8,2,1,5]                 ->  4   (i=1, j=5)
A = [9,8,1,0,1,9,4,0,4,1]         ->  7   (i=2, j=9)
```

**Constraints:** `2 <= len(A) <= 5*10^4`, `0 <= A[i] <= 5*10^4`.
