Given an undirected graph as adjacency lists (`graph[u]` lists the neighbours of
node `u`), return **`true` if the graph is bipartite** — its nodes can be 2-colored
so that every edge joins nodes of different colors — and `false` otherwise.

## Constraints
- `1 <= len(graph) <= 1000`.
- `graph[u]` contains distinct nodes, never `u`, and the graph is symmetric.

## Examples
Input: `graph = [[1,3],[0,2],[1,3],[0,2]]`
Output: `true`
Explanation: color `{0,2}` vs `{1,3}`.

Input: `graph = [[1,2,3],[0,2],[0,1,3],[0,2]]`
Output: `false`

Input: `graph = [[]]`
Output: `true`
