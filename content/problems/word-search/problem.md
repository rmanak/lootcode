Given an `m x n` grid of characters `board` and a string `word`, return **`true`
if `word` can be spelled out from sequentially adjacent cells**, where adjacent
cells neighbour horizontally or vertically. The same cell may not be used more
than once in a single match.

## Constraints
- `m == len(board)`, `n == len(board[0])`, `1 <= m, n <= 6`
- `1 <= len(word) <= 15`
- `board` and `word` consist of English letters

## Examples
![Example 1: the path spelling ABCCED](/problems/word-search/assets/example-1.svg)

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCCED"`
Output: `true`

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "SEE"`
Output: `true`

Input: `board = [["A","B","C","E"],["S","F","C","S"],["A","D","E","E"]], word = "ABCB"`
Output: `false`
Explanation: the second `B` would reuse the only `B` cell.
