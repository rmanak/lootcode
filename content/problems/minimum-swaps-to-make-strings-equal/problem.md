`s1` and `s2` are equal-length strings of `'x'` and `'y'`. In one move you swap some
`s1[i]` with some `s2[j]`. **Return the minimum number of swaps to make `s1 == s2`,
or `-1` if impossible.**

**Examples**
```
s1 = "xx", s2 = "yy"   ->  1
s1 = "xy", s2 = "yx"   ->  2
s1 = "xx", s2 = "xy"   ->  -1
```

**Constraints:** `1 <= len(s1) == len(s2) <= 1000`, characters `'x'`/`'y'`.
