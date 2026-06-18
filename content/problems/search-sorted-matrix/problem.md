Each row of `matrix` is sorted left-to-right, and the first value of every row is
greater than the last value of the previous row — so the whole matrix is sorted if
read row by row. Return **`true` if `target` appears in the matrix**, otherwise
`false`. Aim for `O(log(m*n))` time.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 500`
- `-10^9 <= matrix[i][j], target <= 10^9`

## Examples
Input: `matrix = [[1,3,5],[7,9,11]], target = 9`
Output: `true`
Explanation: `9` sits at row 1, column 1.

Input: `matrix = [[1,3,5],[7,9,11]], target = 4`
Output: `false`
Explanation: No cell holds `4`.
