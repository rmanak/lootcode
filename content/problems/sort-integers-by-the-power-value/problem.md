The *power* of `x` is the number of Collatz steps to reach `1` (`x -> x/2` if even,
`x -> 3x+1` if odd). Sort the integers in `[lo, hi]` by power ascending, breaking ties
by the integer value ascending. **Return the `k`-th integer (1-indexed) in that order.**

**Examples**
```
lo = 12, hi = 15, k = 2  ->  13
lo = 7, hi = 11, k = 4   ->  7
lo = 1, hi = 1000, k = 777  ->  570
```

**Constraints:** `1 <= lo <= hi <= 1000`, `1 <= k <= hi - lo + 1`.
