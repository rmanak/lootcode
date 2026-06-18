`graph` is a directed graph given as an adjacency list (`graph[i]` lists the nodes
`i` points to). A node is **safe** if every path starting from it eventually reaches
a terminal node (one with no outgoing edges) — equivalently, it cannot reach a
cycle. Return all safe nodes in **ascending** order.

## Constraints
- `1 <= len(graph) <= 10^4`
- `graph[i]` contains distinct targets in `0..len(graph)-1`

## Examples
Input: `graph = [[1,2],[2,3],[5],[0],[5],[],[]]`
Output: `[2,4,5,6]`
Explanation: Nodes 5 and 6 are terminal; 2 and 4 only reach them.

Input: `graph = [[1],[2],[0]]`
Output: `[]`
Explanation: All nodes sit on a directed cycle.
