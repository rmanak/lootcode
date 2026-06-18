Given a directed acyclic graph of `n` nodes where `graph[i]` lists the nodes reachable
by a direct edge from `i`, return **all** paths from node `0` to node `n - 1`. The
paths may be returned in any order, but the nodes within each path must stay in
traversal order.

**Example**
```
graph = [[1,2],[3],[3],[]]   ->  [[0,1,3],[0,2,3]]
```

**Constraints:** `2 <= n <= 15`; the graph is acyclic.
