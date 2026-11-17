You are given an `m x n` grid of `0`s (open cells) and `1`s (walls). You start
at the top-left cell `(0, 0)` and want to reach the bottom-right cell
`(m - 1, n - 1)`. Each **move** takes you one cell up, down, left or right, and
you may never leave the grid.

You have two budgets:

- `nMoves`: the total number of moves you may make.
- `nRemove`: the total number of walls you may remove.

Stepping onto an open cell costs **one move**. Stepping onto a wall costs **one
move and one removal**, because the wall is cleared (turned into a `0`) as you
step onto it. A cleared wall stays open, so walking onto it again later costs
only a move.

Return **`true` if you can reach the bottom-right cell using at most `nMoves`
moves and at most `nRemove` removals**, and `false` otherwise. If the grid is a
single cell, you are already there and the answer is `true`.

## Constraints
- `m == grid.length`, `n == grid[i].length`
- `1 <= m, n <= 40`
- `grid[i][j]` is `0` or `1`
- `grid[0][0] == 0`
- `0 <= nMoves <= 10^4`
- `0 <= nRemove <= m * n`

## Examples
Input: `grid = [[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]], nMoves = 6, nRemove = 1`
Output: `true`
Explanation: Go right twice, then break through the wall at `(3, 2)`:
`(0,0) → (0,1) → (0,2) → (1,2) → (2,2) → (3,2) → (4,2)` takes 6 moves and
1 removal. Without any removal the shortest route needs 10 moves.

Input: `grid = [[0,0,0],[1,1,0],[0,0,0],[0,1,1],[0,0,0]], nMoves = 5, nRemove = 1`
Output: `false`
Explanation: Every route needs at least `m + n - 2 = 6` moves.

Input: `grid = [[0,1,1],[1,1,1],[1,0,0]], nMoves = 4, nRemove = 1`
Output: `false`
Explanation: Every route from the start leaves through a wall and then needs to
cross at least one more, so 2 removals are required.
