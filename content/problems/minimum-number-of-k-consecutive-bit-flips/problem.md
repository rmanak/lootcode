`A` contains only `0`s and `1`s. A **K-bit flip** chooses a contiguous subarray of
length `K` and flips every bit in it (`0<->1`). Return the minimum number of K-bit
flips so that `A` contains no `0`, or `-1` if it is impossible.

**Examples**
```
A = [0,1,0], K = 1              ->  2
A = [1,1,0], K = 2              ->  -1
A = [0,0,0,1,0,1,1,0], K = 3    ->  3
```

**Constraints:** `1 <= len(A) <= 3*10^4`, `1 <= K <= len(A)`.
