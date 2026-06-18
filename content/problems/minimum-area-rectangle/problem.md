Given distinct points in the plane, find the minimum area of a rectangle whose sides
are parallel to the axes and whose four corners are all among the points. Return `0`
if no such rectangle exists.

**Examples**
```
points = [[1,1],[1,3],[3,1],[3,3],[2,2]]            ->  4
points = [[1,1],[1,3],[3,1],[3,3],[4,1],[4,3]]      ->  2
```

**Constraints:** `1 <= len(points) <= 500`, `0 <= coordinate <= 4*10^4`, points are
distinct.
