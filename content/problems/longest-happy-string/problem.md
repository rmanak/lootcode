A string is **happy** if it contains none of `"aaa"`, `"bbb"`, or `"ccc"` as a
substring. Using at most `a` copies of `'a'`, `b` of `'b'`, and `c` of `'c'`,
return the **length of the longest possible happy string** (it is `0` if no
non-empty happy string can be built).

**Examples**
```
a = 1, b = 1, c = 7   ->  8     (e.g. "ccaccbcc")
a = 2, b = 2, c = 1   ->  5     (e.g. "aabbc")
a = 7, b = 1, c = 0   ->  5     (e.g. "aabaa")
```

**Constraints:** `0 <= a, b, c <= 100` and `a + b + c > 0`.
