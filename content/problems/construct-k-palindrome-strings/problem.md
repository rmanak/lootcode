**Return `true` if all the characters of `s` can be used to build exactly `k`
non-empty palindrome strings**, else `false`. (Possible iff `k <= len(s)` and the
number of characters with odd frequency is at most `k`.)

**Examples**
```
s = "annabelle", k = 2  ->  true
s = "leetcode", k = 3    ->  false
s = "true", k = 4        ->  true
s = "cr", k = 7          ->  false
```

**Constraints:** `1 <= len(s) <= 10^5`, lowercase letters, `1 <= k <= 10^5`.
