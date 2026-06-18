Split some of the `rods` into two disjoint groups of **equal sum** (welding the rods
in each group). **Return the largest achievable equal sum** (each group's total
height), or `0` if no nonempty equal split exists.

**Examples**
```
rods = [1,2,3,6]      ->  6
rods = [1,2,3,4,5,6]  ->  10
rods = [1,2]          ->  0
```

**Constraints:** `0 <= len(rods) <= 20`, `1 <= rods[i] <= 1000`, `sum <= 5000`.
