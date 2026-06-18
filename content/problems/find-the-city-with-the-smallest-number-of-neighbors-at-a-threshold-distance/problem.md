There are `n` cities `0..n-1`. Each `edges[i] = [a, b, w]` is a bidirectional road of
weight `w`. For a threshold `distanceThreshold`, find the city that can reach the
**fewest** other cities within total path distance `<= distanceThreshold`. If several
cities tie, return the one with the **greatest** index.

**Examples**
```
n = 4, edges = [[0,1,3],[1,2,1],[1,3,4],[2,3,1]], distanceThreshold = 4   ->  3
n = 5, edges = [[0,1,2],[0,4,8],[1,2,3],[1,4,2],[2,3,1],[3,4,1]], distanceThreshold = 2 -> 0
```

**Constraints:** `2 <= n <= 100`, `0 <= a < b < n`, `1 <= w, distanceThreshold <= 10^4`.
