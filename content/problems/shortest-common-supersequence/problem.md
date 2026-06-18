A *common supersequence* of `str1` and `str2` is a string that has both as
subsequences. **Return the length of the shortest common supersequence**, which
equals `len(str1) + len(str2) - LCS(str1, str2)`.

**Examples**
```
str1 = "abac", str2 = "cab"   ->  5    (e.g. "cabac")
str1 = "abc",  str2 = "abc"   ->  3
str1 = "abc",  str2 = "def"   ->  6
```

**Constraints:** `1 <= len(str1), len(str2) <= 1000`, lowercase letters.
