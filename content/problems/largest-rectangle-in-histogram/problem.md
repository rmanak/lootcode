Given an array `heights` of non-negative bar heights (each bar has width 1),
return **the area of the largest rectangle** that fits entirely under the
histogram using contiguous bars.

## Constraints
- `0 <= len(heights) <= 10^5`.
- `0 <= heights[i] <= 10^4`.

## Examples
Input: `heights = [2,1,5,6,2,3]`
Output: `10`
Explanation: bars `5,6` give `2 * 5 = 10`.

Input: `heights = [2,4]`
Output: `4`

Input: `heights = [1,1,1,1]`
Output: `4`
