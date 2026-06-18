A **mountain array** `nums` strictly increases to a single peak and then strictly
decreases. Return **the index of the peak element** (the unique maximum). Aim for
`O(log n)`.

## Constraints
- `1 <= len(nums) <= 10^5`.
- `nums` strictly increases then strictly decreases; values are distinct.

## Examples
Input: `nums = [1,3,5,4,2]`
Output: `2`

Input: `nums = [10]`
Output: `0`

Input: `nums = [1,2,3,4]`
Output: `3`
Explanation: a strictly increasing array peaks at its last index.
