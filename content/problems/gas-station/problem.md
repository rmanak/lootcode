On a circular route, station `i` has `gas[i]` fuel and it costs `cost[i]` to drive to
station `i+1`. Starting with an empty tank, **return the starting station index from
which you can complete the full circuit**, or `-1` if impossible. (A solution, if it
exists, is unique.)

**Examples**
```
gas = [1,2,3,4,5], cost = [3,4,5,1,2]  ->  3
gas = [2,3,4], cost = [3,4,3]          ->  -1
```

**Constraints:** `1 <= len(gas) == len(cost) <= 10^5`, `0 <= gas[i], cost[i]`.
