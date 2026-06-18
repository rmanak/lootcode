A die shows `1`-`6`; face `i` (1-indexed) may not appear more than `rollMax[i-1]`
times **consecutively**. **Return the number of distinct sequences of exactly `n`
rolls**, modulo `10^9 + 7`.

**Examples**
```
n = 2, rollMax = [1,1,2,2,2,3]  ->  34
n = 2, rollMax = [1,1,1,1,1,1]  ->  30
n = 3, rollMax = [1,1,1,2,2,3]  ->  181
```

**Constraints:** `1 <= n <= 5000`, `len(rollMax) == 6`, `1 <= rollMax[i] <= 15`.
