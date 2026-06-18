`grid[r][c]` is the elevation of cell `(r, c)`. At time `t` you may stand on any cell
with elevation `<= t`, and you swim instantly between 4-directionally adjacent
available cells. Return the **least time** `t` at which you can travel from the
top-left to the bottom-right cell. `grid` is `n x n` and is a permutation of
`0..n*n-1`.

## Constraints
- `1 <= n <= 50`
- `grid` is an `n x n` permutation of `0 .. n*n-1`

## Examples
Input: `grid = [[0,2],[1,3]]`
Output: `3`
Explanation: The destination has elevation 3, reachable only once `t = 3`.

Input: `grid = [[0,1,2],[5,4,3],[6,7,8]]`
Output: `8`
Explanation: Every route must eventually cross elevation `8`.
