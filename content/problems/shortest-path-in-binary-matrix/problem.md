Given an `n x n` binary grid where `0` is open and `1` is blocked, return **the
length (number of cells) of the shortest clear path** from the top-left cell to
the bottom-right cell, moving in any of the 8 directions through open cells.
Return `-1` if no such path exists.

## Constraints
- `1 <= n <= 100`.
- Each cell is `0` or `1`.

## Examples
Input: `grid = [[0,1],[1,0]]`
Output: `2`

Input: `grid = [[0,0,0],[1,1,0],[1,1,0]]`
Output: `4`

Input: `grid = [[1,0,0],[1,1,0],[1,1,0]]`
Output: `-1`
Explanation: the start cell is blocked.
