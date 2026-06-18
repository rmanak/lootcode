Each attack at time `timeSeries[i]` poisons for `duration` seconds (overlaps do not
stack). Given the strictly increasing `timeSeries` and `duration`, **return the
total time spent poisoned.**

**Examples**
```
timeSeries = [1,4], duration = 2  ->  4
timeSeries = [1,2], duration = 2  ->  3
```

**Constraints:** `0 <= len(timeSeries) <= 10^4`, strictly increasing,
`0 <= duration <= 10^7`.
