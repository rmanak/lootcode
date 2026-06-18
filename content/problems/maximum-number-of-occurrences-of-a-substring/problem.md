Given a string `s`, **return the maximum number of occurrences** of any substring
that satisfies both rules:

- it contains at most `maxLetters` distinct characters, and
- its length is between `minSize` and `maxSize` inclusive.

(Occurrences may overlap. Only the size-`minSize` substrings ever need to be
counted, since any qualifying longer substring occurs no more often than its
prefix.)

**Examples**
```
s = "aababcaab", maxLetters = 2, minSize = 3, maxSize = 4  ->  2   ("aab" twice)
s = "aaaa",      maxLetters = 1, minSize = 3, maxSize = 3  ->  2   ("aaa" twice)
s = "abcde",     maxLetters = 2, minSize = 3, maxSize = 3  ->  0
```

**Constraints:** `1 <= len(s) <= 10^5`, `1 <= maxLetters <= 26`,
`1 <= minSize <= maxSize <= min(26, len(s))`, lowercase letters only.
