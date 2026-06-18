Given `n` vertices labeled `0..n-1` and a list of undirected `edges`, return the
number of **connected components** in the graph.

## Constraints
- `1 <= n <= 2000`
- `0 <= len(edges) <= n*(n-1)/2`, each `edges[i] = [u, v]` with `u != v`, no
  duplicate edges

## Examples
Input: `n = 5, edges = [[0,1],[1,2],[3,4]]`
Output: `2`
Explanation: Components `{0,1,2}` and `{3,4}`.

Input: `n = 3, edges = []`
Output: `3`
Explanation: Every vertex is isolated.
