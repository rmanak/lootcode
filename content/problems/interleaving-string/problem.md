**Return `true` if `s3` is an interleaving of `s1` and `s2`** — that is, `s3` can be
formed by merging `s1` and `s2` while preserving the left-to-right order of each.

**Examples**
```
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbcbcac"  ->  true
s1 = "aabcc", s2 = "dbbca", s3 = "aadbbbaccc"  ->  false
```

**Constraints:** `0 <= len(s1), len(s2) <= 100`, `len(s3) == len(s1)+len(s2)` (else
`false`), lowercase letters.
