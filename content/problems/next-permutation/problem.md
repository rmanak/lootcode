Given an array `nums`, rearrange it into **the next lexicographically greater
permutation of its elements** and return the result. If no greater permutation
exists (the array is in descending order), return the smallest permutation
(ascending order). Use `O(1)` extra space.

## Constraints
- `1 <= len(nums) <= 10^4`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [1,2,3]`
Output: `[1,3,2]`

Input: `nums = [3,2,1]`
Output: `[1,2,3]`

Input: `nums = [1,1,5]`
Output: `[1,5,1]`
