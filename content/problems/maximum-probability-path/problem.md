An undirected graph on `n` nodes has edges `edges[i] = [a, b]` that succeed with
probability `succProb[i]`. Return the **maximum probability** of reaching `end` from
`start` (the product of edge probabilities along a path), or `0` if `end` is
unreachable. Round the answer to **5 decimal places**.

## Constraints
- `2 <= n <= 10^4`
- `0 <= succProb[i] <= 1`

## Examples
Input: `n = 3, edges = [[0,1],[1,2],[0,2]], succProb = [0.5,0.5,0.2], start = 0, end = 2`
Output: `0.25`
Explanation: `0 -> 1 -> 2` gives `0.5*0.5 = 0.25`, beating the direct `0.2`.

Input: `n = 3, edges = [[0,1]], succProb = [0.5], start = 0, end = 2`
Output: `0.0`
Explanation: Node `2` is unreachable.
