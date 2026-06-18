For a string `t`, `countUniqueChars(t)` is the number of characters that appear
**exactly once** in `t` (e.g. `countUniqueChars("LEETCODE") = 5`: `L, T, C, O, D`).
**Return the sum of `countUniqueChars(t)` over every substring `t` of `s`** (repeated
substrings are counted each time they occur), modulo `10^9 + 7`.

**Examples**
```
s = "ABC"       ->  10
s = "ABA"       ->  8
s = "LEETCODE"  ->  92
```

**Constraints:** `0 <= len(s) <= 10^4`, `s` is upper-case English letters.
