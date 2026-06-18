Given an `m x n` 2D binary grid `grid` of `'1'`s (land) and `'0'`s (water), return
**the number of islands**. An island is formed by connecting adjacent land cells
**horizontally or vertically** and is surrounded by water; assume all four edges
of the grid are surrounded by water.

## Constraints
- `m == len(grid)`, `n == len(grid[0])`, `1 <= m, n <= 300`
- `grid[i][j]` is `'0'` or `'1'`

## Examples
![Example 1: one connected island](/problems/number-of-islands/assets/example-1.svg)

Input: `grid = [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]`
Output: `1`

![Example 2: three separate islands](/problems/number-of-islands/assets/example-2.svg)

Input: `grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]`
Output: `3`
