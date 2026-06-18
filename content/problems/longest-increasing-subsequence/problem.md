Given an integer array `nums`, return **the length of the longest strictly
increasing subsequence**. A subsequence keeps the original order but may drop
elements.

## Constraints
- `1 <= len(nums) <= 2500`
- `-10^4 <= nums[i] <= 10^4`

## Examples
Input: `nums = [10,9,2,5,3,7,101,18]`
Output: `4`
Explanation: One longest increasing subsequence is `[2,3,7,101]`.

Input: `nums = [0,1,0,3,2,3]`
Output: `4`

Input: `nums = [7,7,7,7,7,7,7]`
Output: `1`
Explanation: No two equal values form a *strictly* increasing pair.
