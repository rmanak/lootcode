Two robots start at the top-left `(0,0)` and top-right `(0,cols-1)` of `grid` and
move down to the bottom row; each step goes down-left, down, or down-right. A cell's
cherries are collected when a robot enters it (counted once if both robots share a
cell). Return the **maximum cherries** the two robots collect together.

## Constraints
- `1 <= rows, cols <= 70`
- `0 <= grid[i][j] <= 100`

## Examples
Input: `grid = [[3,1,1],[2,5,1],[1,5,5],[2,1,1]]`
Output: `24`
Explanation: The robots take complementary paths collecting `24` cherries.

Input: `grid = [[1,0,0,0,0,0,1],[2,0,0,0,0,3,0]]`
Output: `7`
Explanation: Robot 1 takes `(0,0)=1, (1,0)=2`; robot 2 takes `(0,6)=1, (1,5)=3`;
together `1 + 1 + 2 + 3 = 7`.
