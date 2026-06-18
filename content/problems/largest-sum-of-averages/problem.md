Partition `A` into at most `K` non-empty **adjacent** groups. The score is the sum of
the averages of the groups. **Return the largest possible score, rounded to 5 decimal
places.** (Answers within `1e-6` are accepted.)

**Example**
```
A = [9,1,2,3,9], K = 3  ->  20.00000   (groups [9], [1,2,3], [9]: 9 + 2 + 9)
```

**Constraints:** `1 <= len(A) <= 100`, `1 <= A[i] <= 10^4`, `1 <= K <= len(A)`.
