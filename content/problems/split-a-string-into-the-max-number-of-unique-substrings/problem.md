Split `s` into non-empty substrings whose concatenation is `s` and which are all
**distinct**. **Return the maximum number of substrings** such a split can have.

**Examples**
```
s = "ababccc"  ->  5    (e.g. ['a','b','ab','c','cc'])
s = "aba"      ->  2
s = "aa"       ->  1
```

**Constraints:** `1 <= len(s) <= 16`, lowercase letters.
