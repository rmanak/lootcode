`A` is a permutation of `0..N-1`. Starting from index `i`, the set `S` collects
`A[i], A[A[i]], A[A[A[i]]], ...` until a value repeats. **Return the length of the
longest such set over all starting indices.**

**Example**
```
A = [5,4,0,3,1,6,2]  ->  4
```

**Constraints:** `1 <= N <= 2*10^4`, `A` is a permutation of `0..N-1`.
