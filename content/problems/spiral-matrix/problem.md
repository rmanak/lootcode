Given an `m x n` `matrix`, return **all of its elements in spiral order** — starting
at the top-left and winding clockwise inward.

![Example 1: spiral traversal of a 3x3 matrix](/problems/spiral-matrix/assets/example-1.svg)

## Constraints
- `m == len(matrix)`, `n == len(matrix[i])`
- `1 <= m, n <= 10`
- `-100 <= matrix[i][j] <= 100`

## Examples
Input: `matrix = [[1,2,3],[4,5,6],[7,8,9]]`
Output: `[1,2,3,6,9,8,7,4,5]`

![Example 2: spiral traversal of a 3x4 matrix](/problems/spiral-matrix/assets/example-2.svg)

Input: `matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]`
Output: `[1,2,3,4,8,12,11,10,9,5,6,7]`
