A robot starts at the top-left cell of an `m x n` grid and wants to reach the
bottom-right cell. At each step it may move **only right or down**. Return **the
number of distinct paths**.

![Example 1: a 3x7 grid with the start, finish, and one sample path](/problems/unique-paths/assets/example-1.svg)

## Constraints
- `1 <= m, n <= 100`
- The answer is guaranteed to be at most `2 * 10^9`.

## Examples
Input: `m = 3, n = 7`
Output: `28`

Input: `m = 3, n = 2`
Output: `3`
Explanation: Down-Down-Right, Down-Right-Down, and Right-Down-Down.
