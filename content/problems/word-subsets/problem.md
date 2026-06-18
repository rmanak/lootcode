For two words `a` and `b`, say `b` is a *subset* of `a` if every letter of `b` occurs
in `a`, counting multiplicity (so `"wrr"` is a subset of `"warrior"` but not of
`"world"`). A word `a` in `A` is **universal** if every word `b` in `B` is a subset of
`a`. Return all universal words of `A`, **in the order they appear in `A`**.

**Examples**
```
A = ["amazon","apple","facebook","google","leetcode"], B = ["e","o"]
   ->  ["facebook","google","leetcode"]
A = ["amazon","apple","facebook","google","leetcode"], B = ["lo","eo"]
   ->  ["google","leetcode"]
```

**Constraints:** `1 <= len(A), len(B) <= 10^4`, `1 <= len(A[i]), len(B[i]) <= 10`.
