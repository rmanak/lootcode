You may repeatedly **double** any odd element or **halve** any even element, any
number of times. Return the **minimum possible deviation** — the smallest achievable
difference between the maximum and minimum element of the array.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,2,3,4]`
Output: `1`
Explanation: Transform to `[2,2,3,4] -> ... -> [3,3,3,4]`-style values with deviation `1`.

Input: `nums = [4,1,5,20,3]`
Output: `3`
Explanation: The smallest reachable max-minus-min is `3`.
