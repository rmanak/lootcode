Given an array `A` of positive integers (not necessarily distinct), return the
**lexicographically largest** permutation that is strictly smaller than `A` and can be
obtained with a single swap of two elements. If no such permutation exists, return `A`
unchanged.

**Examples**
```
A = [3,2,1]      ->  [3,1,2]
A = [1,1,5]      ->  [1,1,5]
A = [1,9,4,6,7]  ->  [1,7,4,6,9]
```

**Constraints:** `1 <= len(A) <= 10^4`, `1 <= A[i] <= 10^4`.
