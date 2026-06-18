A network has `n` nodes labelled `1..n`. Each `times[i] = [u, v, w]` is a directed
edge along which a signal takes `w` time to travel from `u` to `v`. Sending a
signal from node `k`, return **the time for all `n` nodes to receive it**, or `-1`
if some node is unreachable.

## Constraints
- `1 <= n <= 100`, `0 <= len(times) <= n*(n-1)`.
- `1 <= u, v <= n`, `u != v`, `1 <= w <= 100`.

## Examples
Input: `times = [[2,1,1],[2,3,1],[3,4,1]], n = 4, k = 2`
Output: `2`

Input: `times = [[1,2,1]], n = 2, k = 1`
Output: `1`

Input: `times = [[1,2,1]], n = 2, k = 2`
Output: `-1`
