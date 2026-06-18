Run-length encoding replaces each maximal run of a repeated character with the
character followed by the run length (a single character stays as-is, e.g. `"aabccc"`
-> `"a2bc3"`). Deleting **at most `k`** characters from `s`, **return the minimum
possible length** of the run-length encoding of what remains.

**Examples**
```
s = "aaabcccd", k = 2     ->  4    (delete b,d -> "a3c3")
s = "aabbaa", k = 2        ->  2    (delete the b's -> "a4")
s = "aaaaaaaaaaa", k = 0   ->  3    ("a11")
```

**Constraints:** `1 <= len(s) <= 100`, `0 <= k <= len(s)`, lowercase letters.
