Senators are `'R'` (Radiant) or `'D'` (Dire), given in round order by the string
`senate`. Each active senator, in order, may ban one opposing senator (removing them
permanently) or, if only their own party remains active, declare victory. With
optimal play, **return `"Radiant"` or `"Dire"` for the winning party.**

**Examples**
```
senate = "RD"   ->  "Radiant"
senate = "RDD"  ->  "Dire"
```

**Constraints:** `1 <= len(senate) <= 10^4`, characters `'R'`/`'D'`.
