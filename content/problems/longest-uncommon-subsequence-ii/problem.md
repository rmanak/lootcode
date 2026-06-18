A *longest uncommon subsequence* is a string that is a subsequence of exactly one
of the given strings and **not** a subsequence of any other. Given the list `strs`,
**return the length of the longest uncommon subsequence**, or `-1` if none exists.
(Every string is a subsequence of itself.)

**Example**
```
strs = ["aba","cdc","eae"]  ->  3
strs = ["aaa","aaa","aa"]   ->  -1
```

**Constraints:** `2 <= len(strs) <= 50`, `1 <= len(strs[i]) <= 10`, lowercase
letters.
