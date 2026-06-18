A string can be turned into a *scramble* by recursively splitting it into two
non-empty parts and optionally swapping them, applied at any node. Given `s1` and
`s2` of equal length, **return `true` if `s2` is a scramble of `s1`**.

**Examples**
```
s1 = "great", s2 = "rgeat"  ->  true
s1 = "abcde", s2 = "caebd"  ->  false
s1 = "a",     s2 = "a"      ->  true
```

**Constraints:** `1 <= len(s1) == len(s2) <= 30`, lowercase letters.
