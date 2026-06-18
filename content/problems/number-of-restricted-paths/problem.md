An undirected weighted graph has nodes `1..n`; `edges[i] = [u, v, w]`. Let `dist(x)`
be the shortest-path distance from `x` to node `n`. A **restricted path** goes from
node `1` to node `n` such that `dist` strictly **decreases** at every step. Return
the number of restricted paths, modulo `10^9 + 7`.

## Constraints
- `1 <= n <= 2*10^4`
- the graph is connected with positive weights

## Examples
Input: `n = 5, edges = [[1,2,3],[1,3,3],[2,3,1],[1,4,2],[5,2,2],[3,5,1],[5,4,10]]`
Output: `3`
Explanation: Three paths from 1 to 5 strictly decrease distance-to-5.

Input: `n = 3, edges = [[1,2,1],[2,3,1],[1,3,3]]`
Output: `2`
Explanation: `dist(1)=2, dist(2)=1, dist(3)=0`. Both `1 -> 2 -> 3` and the direct
`1 -> 3` strictly decrease distance-to-3.
