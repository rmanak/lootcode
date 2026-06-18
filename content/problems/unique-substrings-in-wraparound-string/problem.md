Let `s` be the infinite wraparound string of `"abcdefghijklmnopqrstuvwxyz"`
(`...zabcdefghi...`). Given a string `p`, return how many **distinct non-empty
substrings** of `p` also appear in `s`.

**Examples**
```
p = "a"     ->  1
p = "cac"   ->  2     ("a", "c")
p = "zab"   ->  6     ("z","a","b","za","ab","zab")
```

**Constraints:** `1 <= len(p) <= 10^5`, `p` is lowercase letters.
