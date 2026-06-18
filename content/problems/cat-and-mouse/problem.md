On an undirected graph (`graph[a]` lists the neighbours of `a`), Mouse starts at node
`1` and moves first, Cat starts at node `2`, and the Hole is node `0`. Players
alternate, each moving along one edge; the Cat may never move to the Hole. The Cat
wins if it ever shares Mouse's node; the Mouse wins by reaching the Hole; a repeated
position (same nodes and same player to move) is a draw. With optimal play, **return
`1` if Mouse wins, `2` if Cat wins, `0` for a draw.**

**Example**
```
graph = [[2,5],[3],[0,4,5],[1,4,5],[2,3],[0,2,3]]  ->  0
```

**Constraints:** `3 <= len(graph) <= 50`, `graph[1]` non-empty, `graph[2]` has a
non-zero neighbour.
