Given a binary grid where `1` is land and `0` is water, an **island** is a group
of `1`s connected 4-directionally. Return **the number of cells in the largest
island**, or `0` if there is no land.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 50`.
- Each cell is `0` or `1`.

## Examples
Input: `grid = [[0,1,0,0],[1,1,1,0],[0,1,0,0]]`
Output: `5`

Input: `grid = [[0,0],[0,0]]`
Output: `0`

Input: `grid = [[1]]`
Output: `1`
