A wheel has gondolas holding up to 4 people each; each rotation costs `runningCost`
and each boarding customer pays `boardingCost`. `customers[i]` people arrive just
before rotation `i`; waiting customers board (up to 4) at each rotation. **Return
the minimum number of rotations that maximizes profit**, or `-1` if profit is never
positive.

**Examples**
```
customers = [8,3],   boardingCost = 5, runningCost = 6  ->  3
customers = [10,9,6], boardingCost = 6, runningCost = 4 ->  7
customers = [3,4,0,5,1], boardingCost = 1, runningCost = 92 ->  -1
```

**Constraints:** `1 <= len(customers) <= 10^5`, `0 <= customers[i] <= 50`,
`1 <= boardingCost, runningCost <= 100`.
