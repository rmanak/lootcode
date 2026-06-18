From an index `i` you may jump forward to some `j > i`. On odd-numbered jumps
(1st, 3rd, ...) you go to the `j` with the smallest `A[j]` that is `>= A[i]`; on
even-numbered jumps to the `j` with the largest `A[j]` that is `<= A[i]` (ties broken
by smallest index; sometimes no legal jump exists). An index is *good* if from it you
can reach the last index. **Return the number of good starting indices.**

**Examples**
```
A = [10,13,12,14,15]  ->  2
A = [2,3,1,1,4]       ->  3
A = [5,1,3,4,2]       ->  3
```

**Constraints:** `1 <= len(A) <= 2*10^4`, `0 <= A[i] < 10^5`.
