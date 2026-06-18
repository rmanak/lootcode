There are 8 prison cells in a row (`1` = occupied, `0` = vacant). Each day, a cell
becomes occupied if its two neighbours were both occupied or both vacant, otherwise it
becomes vacant; the two end cells (which lack two neighbours) always become vacant.
Return the state after `N` days.

**Examples**
```
cells = [0,1,0,1,1,0,0,1], N = 7         ->  [0,0,1,1,0,0,0,0]
cells = [1,0,0,1,0,0,1,0], N = 1000000000 ->  [0,0,1,1,1,1,1,0]
```

**Constraints:** `cells.length == 8`, `1 <= N <= 10^9`.
