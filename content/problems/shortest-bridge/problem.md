`grid` is a binary matrix containing **exactly two** islands (4-directionally
connected groups of `1`s). Return the minimum number of `0` cells you must flip to
`1` to connect the two islands into one.

## Constraints
- `2 <= len(grid), len(grid[0]) <= 100`
- exactly two islands are present

## Examples
Input: `grid = [[0,1],[1,0]]`
Output: `1`
Explanation: Flip either water cell to join the two single-cell islands.

Input: `grid = [[1,0,0,1]]`
Output: `2`
Explanation: The two single-cell islands are separated by two water cells, both of
which must be flipped.
