Given an array `nums` and a window size `k`, return **an array of the maximum
value in each contiguous window of length `k`**, from left to right.

## Constraints
- `1 <= k <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,3,-1,-3,5,3,6,7], k = 3`
Output: `[3,3,5,5,6,7]`

Input: `nums = [9,11], k = 2`
Output: `[11]`

Input: `nums = [4,-2], k = 1`
Output: `[4,-2]`
