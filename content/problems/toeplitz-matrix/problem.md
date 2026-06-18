A matrix is **Toeplitz** when every top-left-to-bottom-right diagonal holds a single
repeated value. Return whether `matrix` is Toeplitz.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 300`
- `0 <= matrix[i][j] <= 10^9`

## Examples
Input: `matrix = [[1,2,3],[4,1,2],[5,4,1]]`
Output: `true`
Explanation: Each descending diagonal is constant.

Input: `matrix = [[1,2],[2,2]]`
Output: `false`
Explanation: The main diagonal contains both `1` and `2`.
