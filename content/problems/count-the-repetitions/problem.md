Define `[s, k]` as `s` concatenated `k` times. String `p` *can be obtained from* `q`
if `p` is a subsequence of `q`. With `S1 = [s1, n1]` and `S2 = [s2, n2]`, **return the
maximum integer `M` such that `[S2, M]` can be obtained from `S1`.**

**Example**
```
s1 = "acb", n1 = 4, s2 = "ab", n2 = 2  ->  2
```

**Constraints:** `1 <= len(s1), len(s2) <= 100`, `0 <= n1 <= 10^6`, `1 <= n2 <= 10^6`.
