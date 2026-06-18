Given binary strings `strs` and budgets of `m` zeros and `n` ones, **return the
maximum number of strings you can select** so that the chosen strings together use
at most `m` `0`s and `n` `1`s.

**Examples**
```
strs = ["10","0001","111001","1","0"], m = 5, n = 3  ->  4
strs = ["10","0","1"], m = 1, n = 1                  ->  2
```

**Constraints:** `1 <= len(strs) <= 600`, `1 <= len(strs[i]) <= 100`,
`0 <= m, n <= 100`.
