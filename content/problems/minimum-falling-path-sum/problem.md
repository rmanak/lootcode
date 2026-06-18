A falling path starts at any cell in the top row and chooses one cell per row,
where each step moves to the same column or a diagonally adjacent column in the
next row. Return the **minimum sum** of any falling path through the square
`matrix`.

![Example 1: a minimum falling path through a 3x3 grid](/problems/minimum-falling-path-sum/assets/example-1.svg)

## Constraints
- `1 <= len(matrix) == len(matrix[i]) <= 200`
- `-10^4 <= matrix[i][j] <= 10^4`

## Examples
Input: `matrix = [[2,1,3],[6,5,4],[7,8,9]]`
Output: `13`
Explanation: The path `1 -> 4 -> 8` has the smallest sum, `13`.

Input: `matrix = [[-19,57],[-40,-5]]`
Output: `-59`
Explanation: Take `-19` then `-40`.
