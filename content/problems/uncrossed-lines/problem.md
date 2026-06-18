Write `A` and `B` on two rows. You may connect `A[i]` to `B[j]` with a line when
`A[i] == B[j]`, but lines must not cross and each number joins at most one line.
**Return the maximum number of connecting lines** (this equals the length of the
longest common subsequence).

**Examples**
```
A = [1,4,2], B = [1,2,4]                  ->  2
A = [2,5,1,2,5], B = [10,5,2,1,5,2]       ->  3
A = [1,3,7,1,7,5], B = [1,9,2,5,1]        ->  2
```

**Constraints:** `1 <= len(A), len(B) <= 500`, `1 <= A[i], B[i] <= 2000`.
