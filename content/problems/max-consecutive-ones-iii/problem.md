Given a binary array `nums` and an integer `k`, return the length of the longest
contiguous subarray containing only `1`s after flipping at most `k` zeros to `1`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `nums[i]` is `0` or `1`
- `0 <= k <= len(nums)`

## Examples
Input: `nums = [1,1,1,0,0,0,1,1,1,1,0], k = 2`
Output: `6`
Explanation: Flip the two zeros at indices 4 and 5 (or 9 and 10) for six ones.

Input: `nums = [0,0,1,1,1,0,0], k = 0`
Output: `3`
Explanation: With no flips the longest run of ones has length `3`.
