A network of `n` servers `0..n-1` is connected by undirected `connections`. A
**critical connection** (bridge) is an edge whose removal disconnects the network.
Return all critical connections, each as `[min, max]`, sorted ascending.

## Constraints
- `1 <= n <= 10^5`
- the graph is connected; no duplicate edges or self-loops

## Examples
Input: `n = 4, connections = [[0,1],[1,2],[2,0],[1,3]]`
Output: `[[1,3]]`
Explanation: The triangle `0-1-2` has no bridges; only `1-3` is critical.

Input: `n = 2, connections = [[0,1]]`
Output: `[[0,1]]`
Explanation: Removing the only edge splits the network.
