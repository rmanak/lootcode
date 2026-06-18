`values[i]` is the value of sightseeing spot `i`. The score of a pair `i < j` is
`values[i] + values[j] + i - j` (the two values, minus the distance between them).
**Return the maximum score** over all pairs.

**Example**
```
values = [8,1,5,2,6]  ->  11   (i = 0, j = 2: 8 + 5 + 0 - 2 = 11)
```

**Constraints:** `2 <= len(values) <= 5*10^4`, `1 <= values[i] <= 1000`.
