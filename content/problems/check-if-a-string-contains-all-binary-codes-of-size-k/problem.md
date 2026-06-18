Given a binary string `s` and an integer `k`, **return `true` if every binary
string of length `k` appears as a substring of `s`**, else `false`.

**Examples**
```
s = "00110110", k = 2  ->  true
s = "0110", k = 1       ->  true
s = "0110", k = 2       ->  false   ("00" is missing)
```

**Constraints:** `1 <= len(s) <= 5*10^5`, `s` is `0`/`1`, `1 <= k <= 20`.
