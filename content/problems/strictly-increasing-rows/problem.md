Return how many rows of `matrix` are **strictly increasing** from left to right.

## Constraints
- `1 <= len(matrix), len(matrix[0]) <= 1000`
- `-10^9 <= matrix[i][j] <= 10^9`

## Examples
Input: `matrix = [[1,2,3],[3,2,1],[4,5,6]]`
Output: `2`
Explanation: Rows `0` and `2` strictly increase.

Input: `matrix = [[2,2],[1,3]]`
Output: `1`
Explanation: Row `0` is flat (`2,2`), only row `1` qualifies.
