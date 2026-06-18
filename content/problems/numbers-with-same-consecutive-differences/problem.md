Return all non-negative integers of length `n` such that the absolute difference
between every two consecutive digits equals `k`. No number may have a leading zero
(so `01` is invalid, but the single digit `0` would be valid — note `n >= 2` here).
You may return the answer in **any order**.

**Examples**
```
n = 3, k = 7  ->  [181,292,707,818,929]
n = 2, k = 1  ->  [10,12,21,23,32,34,43,45,54,56,65,67,76,78,87,89,98]
n = 2, k = 0  ->  [11,22,33,44,55,66,77,88,99]
```

**Constraints:** `2 <= n <= 9`, `0 <= k <= 9`.
