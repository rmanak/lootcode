Given an array of **positive** integers `nums` and an integer `k`, return the number
of contiguous subarrays whose product is strictly less than `k`.

## Constraints
- `1 <= len(nums) <= 10^5`
- `1 <= nums[i] <= 1000`
- `0 <= k <= 10^9`

## Examples
Input: `nums = [10,5,2,6], k = 100`
Output: `8`
Explanation: Eight subarrays have product below `100`.

Input: `nums = [1,2,3], k = 0`
Output: `0`
Explanation: A positive product is never below `0`.
