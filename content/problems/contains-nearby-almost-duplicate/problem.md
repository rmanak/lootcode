Return `true` if there exist two indices `i != j` with `|i - j| <= indexDiff` and
`|nums[i] - nums[j]| <= valueDiff`, otherwise `false`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`
- `0 <= indexDiff, valueDiff`

## Examples
Input: `nums = [1,2,3,1], indexDiff = 3, valueDiff = 0`
Output: `true`
Explanation: The two `1`s are 3 indices apart and equal.

Input: `nums = [1,5,9,1,5,9], indexDiff = 2, valueDiff = 3`
Output: `false`
Explanation: No two values within 2 indices differ by at most 3.
