You are given `points`, where `points[i] = [xi, yi]` is an integer coordinate on a
2D plane. The cost of connecting two points is the Manhattan distance between them,
`|xi - xj| + |yi - yj|`. Return the minimum total cost to connect all points so that
there is exactly one simple path between any two points.

**Examples**
```
points = [[0,0],[2,2],[3,10],[5,2],[7,0]]   ->  20
points = [[3,12],[-2,5],[-4,1]]             ->  18
points = [[0,0]]                            ->  0
```

**Constraints:** `1 <= len(points) <= 1000`, `-10^6 <= xi, yi <= 10^6`, points distinct.
