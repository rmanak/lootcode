You start at index `0` of an integer array `nums`; `nums[i]` is the maximum jump
length from index `i`. Return **`true` if you can reach the last index**, otherwise
`false`.

## Constraints
- `1 <= len(nums) <= 10^4`
- `0 <= nums[i] <= 10^5`

## Examples
Input: `nums = [2,3,1,1,4]`
Output: `true`
Explanation: Jump 1 step to index 1, then 3 steps to the last index.

Input: `nums = [3,2,1,0,4]`
Output: `false`
Explanation: You always land on index 3 (value 0) and can move no further.
