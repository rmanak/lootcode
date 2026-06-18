`favoriteCompanies[i]` is the list of companies the i-th person likes. Return, in
**increasing order**, the indices of people whose favorite list is **not** a subset
of any other person's favorite list.

**Examples**
```
[["leetcode","google","facebook"],["google","microsoft"],
 ["google","facebook"],["google"],["amazon"]]            ->  [0,1,4]
[["leetcode","google","facebook"],["leetcode","amazon"],
 ["facebook","google"]]                                  ->  [0,1]
```

**Constraints:** `1 <= len(favoriteCompanies) <= 100`; all lists are distinct.
