Given an `m x n` integer matrix, if an element is `0`, set its **entire row and
column** to `0`. Do it in place and **return the modified matrix**.

## Constraints
- `m == len(matrix)`, `n == len(matrix[0])`, `1 <= m, n <= 200`
- `-2^31 <= matrix[i][j] <= 2^31 - 1`

## Examples
![Example 1: the middle 0 clears its row and column](/problems/set-matrix-zeroes/assets/example-1.svg)

Input: `matrix = [[1,1,1],[1,0,1],[1,1,1]]`
Output: `[[1,0,1],[0,0,0],[1,0,1]]`

![Example 2](/problems/set-matrix-zeroes/assets/example-2.svg)

Input: `matrix = [[0,1,2,0],[3,4,5,2],[1,3,1,5]]`
Output: `[[0,0,0,0],[0,4,5,0],[0,3,1,0]]`
