A *happy string* uses only `'a'`, `'b'`, `'c'` and never repeats a letter in
adjacent positions. List all happy strings of length `n` in lexicographic order.
**Return the `k`-th string in that list (1-indexed)**, or `""` if fewer than `k`
exist.

**Examples**
```
n = 1, k = 3   ->  "c"
n = 1, k = 4   ->  ""
n = 3, k = 9   ->  "cab"
n = 10, k = 100 -> "abacbabacb"
```

**Constraints:** `1 <= n <= 10`, `1 <= k <= 100`.
