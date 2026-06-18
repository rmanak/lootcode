For each `multipliers[i]` in order, take a number from **either end** of `nums`,
multiply it by `multipliers[i]`, and add it to your score. After all `m`
multipliers, return the **maximum total score**.

## Constraints
- `1 <= len(multipliers) <= 300 <= len(nums) <= 10^5`
- `-1000 <= nums[i], multipliers[i] <= 1000`

## Examples
Input: `nums = [1,2,3], multipliers = [3,2,1]`
Output: `14`
Explanation: `3*3 + 2*2 + 1*1 = 14`.

Input: `nums = [-5,-3,-3,-2,7,1], multipliers = [-10,-5,3,4,6]`
Output: `102`
Explanation: Optimal end choices yield `102`.
