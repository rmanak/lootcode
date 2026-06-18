Start from an undirected graph with nodes `0..n-1`. Each entry `edges[k] =
[u, v, cnt]` means the edge `(u, v)` is replaced by a chain that inserts `cnt` new
intermediate nodes between `u` and `v` (so the chain has `cnt + 1` unit-length
edges).

Starting at node `0`, each move travels along one unit edge. Return how many nodes
(original **and** newly inserted) are reachable using at most `maxMoves` moves.

**Examples**
```
edges = [[0,1,10],[0,2,1],[1,2,2]], maxMoves = 6, n = 3   ->  13
edges = [[0,1,4],[1,2,6],[0,2,8],[1,3,1]], maxMoves = 10, n = 4   ->  23
```

**Constraints:** `0 <= len(edges) <= 10^4`, `0 <= cnt <= 10^4`,
`0 <= maxMoves <= 10^9`, `1 <= n <= 3000`.
