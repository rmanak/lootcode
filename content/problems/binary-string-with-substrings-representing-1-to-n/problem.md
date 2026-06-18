Given a binary string `S` (only `'0'` and `'1'`) and a positive integer `N`, return
`True` if and only if, for **every** integer `X` from `1` to `N`, the binary
representation of `X` is a substring of `S`.

**Examples**
```
S = "0110", N = 3   ->  True
S = "0110", N = 4   ->  False
```

**Constraints:** `1 <= len(S) <= 1000`, `1 <= N <= 10^9`.
