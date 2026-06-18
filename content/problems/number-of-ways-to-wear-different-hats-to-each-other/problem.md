There are `n` people and `40` types of hats labeled `1` to `40`. `hats[i]` is the
list of hats preferred by the `i`-th person. **Return the number of ways the `n`
people can each wear a hat such that no two people wear the same hat**, modulo
`10^9 + 7`.

**Examples**
```
hats = [[3,4],[4,5],[5]]                          ->  1
hats = [[3,5,1],[3,5]]                            ->  4
hats = [[1,2,3,4],[1,2,3,4],[1,2,3,4],[1,2,3,4]]  ->  24
```

**Constraints:** `1 <= n <= 10`, `1 <= len(hats[i]) <= 40`,
`1 <= hats[i][j] <= 40`, each `hats[i]` holds distinct integers.
