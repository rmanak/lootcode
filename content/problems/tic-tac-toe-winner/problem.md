On an `n x n` tic-tac-toe board, `moves[i] = [row, col, player]` is applied in order
(player is `1` or `2`). For each move, output the player who has just won (completed
a full row, column, or diagonal), or `0` if no one has won yet. Return one result per
move.

## Constraints
- `1 <= n <= 100`
- moves are valid: distinct cells, players alternate

## Examples
Input: `n = 3, moves = [[0,0,1],[1,1,2],[0,1,1],[2,2,2],[0,2,1]]`
Output: `[0,0,0,0,1]`
Explanation: Player 1 completes the top row on the last move.

Input: `n = 2, moves = [[0,0,2],[1,1,2]]`
Output: `[0,2]`
Explanation: Player 2 completes the main diagonal.
