Given a stream of numbers `nums` processed left to right, return **an array whose
`i`-th entry is the average of the first `i+1` numbers**, each rounded to 5
decimal places.

## Constraints
- `0 <= len(nums) <= 10^5`.
- `-10^6 <= nums[i] <= 10^6`.

## Examples
Input: `nums = [2,4,6]`
Output: `[2.0, 3.0, 4.0]`
Explanation: averages of `[2]`, `[2,4]`, `[2,4,6]`.

Input: `nums = [1,2]`
Output: `[1.0, 1.5]`

Input: `nums = []`
Output: `[]`
