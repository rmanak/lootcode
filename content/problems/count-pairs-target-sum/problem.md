Given an integer array `nums` and an integer `target`, return **the number of
index pairs `(i, j)` with `i < j` such that `nums[i] + nums[j] == target`**.
Pairs are counted by position, so repeated values produce multiple pairs.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^9 <= nums[i], target <= 10^9`.

## Examples
Input: `nums = [1,1,1], target = 2`
Output: `3`
Explanation: the pairs `(0,1)`, `(0,2)`, `(1,2)`.

Input: `nums = [1,2,3,4], target = 5`
Output: `2`

Input: `nums = [5,5], target = 9`
Output: `0`
