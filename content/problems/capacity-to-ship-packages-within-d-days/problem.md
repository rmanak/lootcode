Packages with `weights` must ship in order within `days` days; each day's load can't
exceed the ship's capacity. **Return the least capacity that ships everything within
`days` days.**

**Examples**
```
weights = [1,2,3,4,5,6,7,8,9,10], days = 5  ->  15
weights = [3,2,2,4,1,4], days = 3           ->  6
weights = [1,2,3,1,1], days = 4             ->  3
```

**Constraints:** `1 <= days <= len(weights) <= 5*10^4`, `1 <= weights[i] <= 500`.
