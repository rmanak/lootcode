Houses are arranged in a **circle**, so the first and the last house are
adjacent. House `i` holds `nums[i]` money and you cannot rob two adjacent houses.
Return **the maximum amount of money you can rob**.

## Constraints
- `1 <= len(nums) <= 100`
- `0 <= nums[i] <= 1000`

## Examples
Input: `nums = [2,3,2]`
Output: `3`
Explanation: houses 1 and 3 are adjacent in the circle, so you cannot take both 2s.

Input: `nums = [1,2,3,1]`
Output: `4`

Input: `nums = [1,2,3]`
Output: `3`
