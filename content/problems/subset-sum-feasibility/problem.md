Given an array of non-negative integers `nums` and a non-negative `target`,
return **`true` if some subset of `nums` sums to exactly `target`** (the empty
subset sums to `0`).

## Constraints
- `0 <= len(nums) <= 200`, `0 <= target <= 2*10^4`.
- `0 <= nums[i] <= 1000`.

## Examples
Input: `nums = [3,34,4,12,5,2], target = 9`
Output: `true`
Explanation: `4 + 5 = 9`.

Input: `nums = [3,34,4,12,5,2], target = 30`
Output: `false`

Input: `nums = [1,2,3], target = 0`
Output: `true`
