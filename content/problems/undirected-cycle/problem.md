Given `n` vertices labeled `0..n-1` and a list of undirected `edges` (a simple
graph: no self-loops or duplicate edges), return whether the graph contains a
**cycle**.

## Constraints
- `1 <= n <= 2000`
- each `edges[i] = [u, v]` with `u != v`, no duplicate edges

## Examples
Input: `n = 3, edges = [[0,1],[1,2],[2,0]]`
Output: `true`
Explanation: The three edges form a triangle.

Input: `n = 4, edges = [[0,1],[1,2],[2,3]]`
Output: `false`
Explanation: A path graph has no cycle.
