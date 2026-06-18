Given a list of strings `words` (no string is a substring of another), a
*superstring* is a string that contains every word as a (contiguous) substring.
**Return the length of the shortest possible superstring.**

**Examples**
```
words = ["alex","loves","leetcode"]              ->  17   ("alexlovesleetcode")
words = ["catg","ctaagt","gcta","ttca","atgcatc"] ->  16   ("gctaagttcatgcatc")
```

**Constraints:** `1 <= len(words) <= 12`, `1 <= len(words[i]) <= 20`, lowercase letters.
