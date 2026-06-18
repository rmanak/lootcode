Place `n` queens on an `n x n` board so that no two attack each other (no shared
row, column, or diagonal). Return **all distinct solutions**; each solution is a
list of `n` strings, where each string is a board row using `'Q'` for a queen and
`'.'` for an empty cell. Solutions may be returned in any order.

## Constraints
- `1 <= n <= 9`.

## Examples
Input: `n = 4`
Output: `[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]`

Input: `n = 1`
Output: `[["Q"]]`

Input: `n = 2`
Output: `[]`
Explanation: two queens always attack on a 2x2 board.
