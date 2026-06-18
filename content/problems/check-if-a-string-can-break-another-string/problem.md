String `x` *breaks* string `y` (same length) if `x[i] >= y[i]` for every `i` after
each is permuted. **Return `true` if some permutation of `s1` can break some
permutation of `s2`, or vice versa.**

**Examples**
```
s1 = "abc", s2 = "xya"        ->  true
s1 = "abe", s2 = "acd"        ->  false
s1 = "leetcodee", s2 = "interview" ->  true
```

**Constraints:** `1 <= len(s1) == len(s2) <= 10^5`, lowercase letters.
