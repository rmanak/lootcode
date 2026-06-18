`grid` is sorted in **non-increasing** order both left-to-right along every row and
top-to-bottom down every column. Return the **count of negative numbers** in the
grid. Aim for `O(m + n)` time.

## Constraints
- `1 <= len(grid), len(grid[0]) <= 1000`
- `-10^9 <= grid[i][j] <= 10^9`

## Examples
Input: `grid = [[4,3,-1],[2,-1,-2],[-1,-2,-3]]`
Output: `6`
Explanation: Six entries are below zero.

Input: `grid = [[3,2],[1,0]]`
Output: `0`
Explanation: Nothing is negative (`0` does not count).
