Given a connected, undirected, weighted graph with `n` nodes `0..n-1` and `edges`
where `edges[i] = [u, v, w]`, return **the total weight of a minimum spanning
tree** (the cheapest set of edges connecting all nodes).

## Constraints
- `1 <= n <= 1000`; the graph is connected.
- `edges[i] = [u, v, w]`, `0 <= u, v < n`, `1 <= w <= 10^6`.

## Examples
Input: `n = 4, edges = [[0,1,10],[0,2,6],[0,3,5],[1,3,15],[2,3,4]]`
Output: `19`
Explanation: pick edges of weight `5 + 4 + 10`.

Input: `n = 2, edges = [[0,1,7]]`
Output: `7`

Input: `n = 1, edges = []`
Output: `0`
