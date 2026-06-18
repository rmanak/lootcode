Alice and Bob alternate turns (Alice first) with `n` stones in a pile. On a turn a
player removes a non-zero **perfect-square** number of stones; a player who cannot
move loses. Both play optimally. **Return `true` if Alice wins.**

**Examples**
```
n = 1  ->  true
n = 2  ->  false
n = 4  ->  true
n = 7  ->  false
```

**Constraints:** `1 <= n <= 10^5`.
