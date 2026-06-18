Row 1 is `0`. Each later row is formed from the previous one by replacing every `0`
with `01` and every `1` with `10`. Given a row number `N` and a **1-indexed** position
`K`, return the symbol at that position.

```
row 1: 0
row 2: 01
row 3: 0110
row 4: 01101001
```

**Examples**
```
N = 1, K = 1  ->  0
N = 2, K = 2  ->  1
N = 4, K = 5  ->  1
```

**Constraints:** `1 <= N <= 30`, `1 <= K <= 2^(N-1)`.
