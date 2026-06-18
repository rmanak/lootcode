Count the pairs of indices `i < j` such that `nums[i] > 2 * nums[j]`. Aim for
`O(n log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,3,2,3,1]`
Output: `2`
Explanation: The pairs are `(i=1,j=4)` with `3 > 2*1` and `(i=3,j=4)` with `3 > 2*1`.

Input: `nums = [2,4,3,5,1]`
Output: `3`
Explanation: `(4,1)`, `(3,1)`, and `(5,1)` each satisfy `nums[i] > 2*nums[j]`.
