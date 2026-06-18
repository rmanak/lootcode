Build a graph whose nodes are the values in `nums` (all distinct); connect two values
if they share a **common factor greater than 1**. Return the size of the largest
connected component.

## Constraints
- `1 <= len(nums) <= 2*10^4`
- `1 <= nums[i] <= 10^5`, values are distinct

## Examples
Input: `nums = [4,6,15,35]`
Output: `4`
Explanation: `4-6` (2), `6-15` (3), `15-35` (5) connect everything.

Input: `nums = [20,50,9,63]`
Output: `2`
Explanation: `20-50` (10) and `9-63` (9) form two size-2 components.
