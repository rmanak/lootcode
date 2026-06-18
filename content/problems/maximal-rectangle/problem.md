Given a binary `matrix`, return the **area of the largest rectangle** whose cells
are all `1`s.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 200`
- `matrix[i][j]` is `0` or `1`

## Examples
Input: `matrix = [[1,0,1],[1,1,1]]`
Output: `3`
Explanation: The bottom row is a `1x3` rectangle of ones.

Input: `matrix = [[0,0],[0,0]]`
Output: `0`
Explanation: There are no `1`s, so the largest rectangle has area `0`.
