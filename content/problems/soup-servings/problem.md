Two soups A and B start with `n` ml each. Each turn one of four operations is chosen
with probability `0.25`, serving `(A,B)` ml of `(100,0)`, `(75,25)`, `(50,50)`, or
`(25,75)` (serve as much as available if short). Stop when at least one soup is
empty. **Return P(A empties first) + 0.5 * P(both empty together)**, rounded to 5
decimals.

**Example**
```
n = 50  ->  0.62500
```

**Constraints:** `0 <= n <= 10^9` (answers within `1e-6` accepted).
