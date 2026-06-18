A *k-duplicate removal* deletes `k` adjacent equal letters, after which the two
sides join. Repeat until no such group remains. **Return the final string** (it is
unique).

**Examples**
```
s = "abcd", k = 2            ->  "abcd"
s = "deeedbbcccbdaa", k = 3  ->  "aa"
s = "pbbcggttciiippooaais", k = 2 ->  "ps"
```

**Constraints:** `1 <= len(s) <= 10^5`, `2 <= k <= 10^4`, lowercase letters.
