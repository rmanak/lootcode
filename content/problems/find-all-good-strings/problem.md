A *good string* has length `n`, is `>= s1` and `<= s2` lexicographically, and does
**not** contain `evil` as a substring. **Return the number of good strings, modulo
`10^9 + 7`.**

**Examples**
```
n = 2, s1 = "aa", s2 = "da", evil = "b"            ->  51
n = 8, s1 = "leetcode", s2 = "leetgoes", evil = "leet" ->  0
n = 2, s1 = "gx", s2 = "gz", evil = "x"            ->  2
```

**Constraints:** `len(s1) == len(s2) == n`, `s1 <= s2`, `1 <= n <= 500`,
`1 <= len(evil) <= 50`, lowercase letters.
