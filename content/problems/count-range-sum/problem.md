Count the number of contiguous subarrays whose sum lies in the inclusive range
`[lower, upper]`. Aim for `O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `lower <= upper`

## Examples
Input: `nums = [-2,5,-1], lower = -2, upper = 2`
Output: `3`
Explanation: The qualifying subarray sums are `-2`, `2`, and `-1`.

Input: `nums = [0], lower = 0, upper = 0`
Output: `1`
Explanation: The single subarray sums to `0`.
