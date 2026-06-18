A program printed an array of integers but forgot the separators, leaving the
digit string `s`. Every original integer was in the range `[1, k]` and had no
leading zero. **Return the number of arrays** that could print as `s`, modulo
`10^9 + 7`.

**Examples**
```
s = "1000", k = 10000  ->  1    (only [1000])
s = "1000", k = 10      ->  0
s = "1317", k = 2000    ->  8
s = "2020", k = 30      ->  1    (only [20,20])
```

**Constraints:** `1 <= len(s) <= 10^5`, `s` is digits with no leading zero,
`1 <= k <= 10^9`.
