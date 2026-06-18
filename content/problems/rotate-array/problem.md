Given an array `nums` and a non-negative integer `k`, rotate the array to the
**right** by `k` positions and return **the resulting array**. Rotations wrap
around, and `k` may exceed the array length.

## Constraints
- `0 <= len(nums) <= 10^5`, `0 <= k <= 10^9`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,2,3,4,5,6,7], k = 3`
Output: `[5,6,7,1,2,3,4]`

Input: `nums = [-1,-100,3,99], k = 2`
Output: `[3,99,-1,-100]`

Input: `nums = [1], k = 5`
Output: `[1]`
