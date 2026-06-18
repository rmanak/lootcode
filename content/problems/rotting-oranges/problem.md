In a grid each cell is `0` (empty), `1` (fresh orange), or `2` (rotten orange).
Every minute, any fresh orange adjacent (4-directionally) to a rotten orange
becomes rotten. Return **the minimum number of minutes until no fresh orange
remains**, or `-1` if some fresh orange can never rot.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 50`.
- Each cell is `0`, `1`, or `2`.

## Examples
Input: `grid = [[2,1,1],[1,1,0],[0,1,1]]`
Output: `4`

Input: `grid = [[2,1,1],[0,1,1],[1,0,1]]`
Output: `-1`
Explanation: the bottom-left orange is never reached.

Input: `grid = [[0,2]]`
Output: `0`
