You are given a string `s` and a list of index `pairs`. You may swap the characters at
any listed pair of indices, any number of times. Return the lexicographically smallest
string reachable.

**Examples**
```
s = "dcab", pairs = [[0,3],[1,2]]         ->  "bacd"
s = "dcab", pairs = [[0,3],[1,2],[0,2]]   ->  "abcd"
s = "cba",  pairs = [[0,1],[1,2]]         ->  "abc"
```

**Constraints:** `1 <= len(s) <= 10^5`, `0 <= len(pairs) <= 10^5`, lowercase letters.
