Each move you remove the leftmost or rightmost element of `nums` and subtract it
from `x`. Return the **minimum number of moves** to make `x` exactly `0`, or `-1`
if it is impossible.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 10^4`
- `1 <= x <= 10^9`

## Examples
Input: `nums = [1,1,4,2,3], x = 5`
Output: `2`
Explanation: Remove `3` then `2` from the right.

Input: `nums = [5,6,7,8,9], x = 4`
Output: `-1`
Explanation: No sequence of end removals sums to `4`.
