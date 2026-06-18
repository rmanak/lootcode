Two players alternate taking a number from **either end** of `nums`, adding it to
their score; both play optimally. Return `true` if **player 1** can end with a score
greater than or equal to player 2.

## Constraints
- `1 <= len(nums) <= 20`
- `0 <= nums[i] <= 10^7`

## Examples
Input: `nums = [1,5,2]`
Output: `false`
Explanation: Player 1 cannot avoid finishing behind.

Input: `nums = [1,5,233,7]`
Output: `true`
Explanation: Player 1 can force at least a tie.
