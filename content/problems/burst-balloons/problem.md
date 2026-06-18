You have balloons with values `nums`. Bursting balloon `i` earns
`left * nums[i] * right` coins, where `left` and `right` are the values of the
currently-adjacent balloons (out-of-range neighbors count as `1`). Return the
**maximum coins** obtainable by bursting all balloons in some order.

## Constraints
- `1 <= len(nums) <= 300`
- `0 <= nums[i] <= 100`

## Examples
Input: `nums = [3,1,5,8]`
Output: `167`
Explanation: Burst order `1, 5, 3, 8` yields `3*1*5 + 3*5*8 + 1*3*8 + 1*8*1 = 167`.

Input: `nums = [1,5]`
Output: `10`
Explanation: Burst `1` (`1*1*5=5`) then `5` (`1*5*1=5`).
