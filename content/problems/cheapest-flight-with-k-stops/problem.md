There are `n` cities `0..n-1` connected by `flights[i] = [u, v, w]` (a flight from
`u` to `v` costing `w`). Return **the cheapest price from `src` to `dst` using at
most `k` stops** (i.e. at most `k+1` flights), or `-1` if no such route exists.

## Constraints
- `1 <= n <= 100`, `0 <= len(flights) <= n*(n-1)`.
- `0 <= u, v < n`, `u != v`, `1 <= w <= 10^4`, `0 <= k < n`.

## Examples
Input: `n = 4, flights = [[0,1,100],[1,2,100],[2,0,100],[1,3,600],[2,3,200]], src = 0, dst = 3, k = 1`
Output: `700`
Explanation: `0→1→3` costs `700` within 1 stop.

Input: `n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k = 1`
Output: `200`

Input: `n = 3, flights = [[0,1,100],[1,2,100],[0,2,500]], src = 0, dst = 2, k = 0`
Output: `500`
