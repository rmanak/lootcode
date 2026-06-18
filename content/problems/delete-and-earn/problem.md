Pick any value `x` from `nums` to earn `x` points, but doing so deletes **every**
occurrence of `x - 1` and `x + 1`. Repeat until `nums` is empty. Return the
**maximum points** you can earn.

## Constraints
- `1 <= len(nums) <= 2*10^4`
- `1 <= nums[i] <= 10^4`

## Examples
Input: `nums = [3,4,2]`
Output: `6`
Explanation: Take `4` (deletes `3`), then `2`, for `4 + 2 = 6`.

Input: `nums = [2,2,3,3,3,4]`
Output: `9`
Explanation: Take all three `3`s (deletes the `2`s and `4`) for `9`.
