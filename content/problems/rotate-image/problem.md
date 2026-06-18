You are given an `n x n` 2D `matrix` representing an image. **Rotate the matrix 90
degrees clockwise, in place, and return it.** Modify the input directly — do not
allocate a second `n x n` matrix.

![Example 1: rotate the 3x3 matrix 90 degrees clockwise](/problems/rotate-image/assets/example-1.svg)

## Constraints
- `n == len(matrix) == len(matrix[i])`
- `1 <= n <= 20`
- `-1000 <= matrix[i][j] <= 1000`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[[7,4,1],[8,5,2],[9,6,3]]`

![Example 2: rotate the 4x4 matrix 90 degrees clockwise](/problems/rotate-image/assets/example-2.svg)

Input: `matrix = [[5,1,9,11],[2,4,8,10],[13,3,6,7],[15,14,12,16]]`
Output: `[[15,13,2,5],[14,3,4,1],[12,6,8,9],[16,7,10,11]]`
