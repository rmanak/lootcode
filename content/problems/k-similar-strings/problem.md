Two anagrams `A` and `B` are *K-similar* if `A` can be turned into `B` by swapping
two characters `K` times. **Return the smallest such `K`.**

**Examples**
```
A = "ab",   B = "ba"    ->  1
A = "abc",  B = "bca"   ->  2
A = "abac", B = "baca"  ->  2
```

**Constraints:** `1 <= len(A) == len(B) <= 20`, `A` and `B` are anagrams over the
letters `a`..`f`.
