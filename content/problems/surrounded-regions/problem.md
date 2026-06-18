`board` holds the letters `"X"` and `"O"`. Capture every region of `"O"`s that is
**not** connected to the border by flipping those cells to `"X"`; regions touching
any edge survive. Return the modified board.

## Constraints
- `1 <= len(board), len(board[0]) <= 200`
- `board[i][j]` is `"X"` or `"O"`

## Examples
Input: `board = [["X","X","X"],["X","O","X"],["X","X","X"]]`
Output: `[["X","X","X"],["X","X","X"],["X","X","X"]]`
Explanation: The single `"O"` is fully surrounded, so it is captured.

Input: `board = [["O","X"],["X","O"]]`
Output: `[["O","X"],["X","O"]]`
Explanation: Both `"O"` cells lie on the border and are safe.
