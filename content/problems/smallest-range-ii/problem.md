To every element of `A` you must add either `+K` or `-K` (exactly once each),
producing an array `B`. **Return the smallest possible value of
`max(B) - min(B)`.**

**Examples**
```
A = [1], K = 0       ->  0
A = [0,10], K = 2    ->  6
A = [1,3,6], K = 3   ->  3
```

**Constraints:** `1 <= len(A) <= 10^4`, `0 <= A[i] <= 10^4`, `0 <= K <= 10^4`.
