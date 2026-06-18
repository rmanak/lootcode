Given a binary `matrix`, return the **total number of square submatrices made up
entirely of `1`s** (squares of every size, counted separately).

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 300`
- `matrix[i][j]` is `0` or `1`

## Examples
Input: `matrix = [[1,1],[1,1]]`
Output: `5`
Explanation: Four `1x1` squares plus one `2x2` square.

Input: `matrix = [[1,0],[0,1]]`
Output: `2`
Explanation: Only the two diagonal `1x1` squares are all ones.
