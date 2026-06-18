`grid` is a binary matrix where `1` is land and `0` is sea. Moving only up, down,
left, or right through land cells, return the **number of land cells from which you
can never walk off the boundary** of the grid.

![Example 1: enclaves are land cells that cannot reach the border](/problems/number-of-enclaves/assets/example-1.svg)

## Constraints
- `1 <= len(grid), len(grid[0]) <= 500`
- `grid[i][j]` is `0` or `1`

## Examples
Input: `grid = [[0,0,0,0],[1,0,1,0],[0,1,1,0],[0,0,0,0]]`
Output: `3`
Explanation: The three central land cells are walled in by sea.

Input: `grid = [[1,0],[0,1]]`
Output: `0`
Explanation: Every land cell already touches the boundary.
