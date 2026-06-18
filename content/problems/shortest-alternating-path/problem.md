A directed graph on `n` nodes has red edges `redEdges` and blue edges `blueEdges`.
For each node `i`, return the length of the shortest path from node `0` to `i` whose
edge colors **alternate** (no two consecutive edges share a color), or `-1` if no
such path exists.

## Constraints
- `1 <= n <= 100`
- each edge is `[from, to]`; parallel/self edges may appear

## Examples
Input: `n = 3, redEdges = [[0,1]], blueEdges = [[1,2]]`
Output: `[0,1,2]`
Explanation: Red `0->1` then blue `1->2`.

Input: `n = 3, redEdges = [[0,1],[1,2]], blueEdges = []`
Output: `[0,1,-1]`
Explanation: Two red edges cannot be used in a row.
