For each index `i`, count how many values to the **right** of `i` are strictly
smaller than `nums[i]`. Return those counts as an array the same length as `nums`.
Aim for `O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [5,2,6,1]`
Output: `[2,1,1,0]`
Explanation: Right of `5` are `2` and `1`; right of `2` is `1`; right of `6` is `1`.

Input: `nums = [-1]`
Output: `[0]`
Explanation: Nothing lies to the right of the only element.
