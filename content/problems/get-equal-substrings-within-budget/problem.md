Changing `s[i]` to `t[i]` costs `abs(ord(s[i]) - ord(t[i]))`. With a total budget of
`maxCost`, **return the maximum length of a substring of `s` that can be transformed
into the corresponding substring of `t`** within budget.

**Examples**
```
s = "abcd", t = "bcdf", maxCost = 3  ->  3
s = "abcd", t = "cdef", maxCost = 3  ->  1
s = "abcd", t = "acde", maxCost = 0  ->  1
```

**Constraints:** `1 <= len(s) == len(t) <= 10^5`, `0 <= maxCost <= 10^6`,
lowercase letters.
