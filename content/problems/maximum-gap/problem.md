Return the **maximum difference between two successive values** once `nums` is
sorted in ascending order. If `nums` has fewer than two elements, return `0`. Aim
for linear time.

## Constraints
- `1 <= len(nums) <= 10^5`
- `0 <= nums[i] <= 10^9`

## Examples
Input: `nums = [3,6,9,1]`
Output: `3`
Explanation: Sorted order is `[1,3,6,9]`; the largest adjacent gap is `3`.

Input: `nums = [10]`
Output: `0`
Explanation: Fewer than two elements means a gap of `0`.
