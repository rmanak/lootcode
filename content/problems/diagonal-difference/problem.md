Given a **square** `matrix`, return the absolute difference between the sum of its
primary diagonal (top-left to bottom-right) and the sum of its secondary diagonal
(top-right to bottom-left).

## Constraints
- `1 <= len(matrix) == len(matrix[i]) <= 1000`
- `-10^4 <= matrix[i][j] <= 10^4`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `0`
Explanation: Both diagonals sum to `15`.

Input: `matrix = [[5,1],[2,3]]`
Output: `5`
Explanation: The diagonals sum to `8` (`5 + 3`) and `3` (`1 + 2`); `|8 - 3| = 5`.
