Given an integer array `nums` and an integer `k`, return **the `k`-th largest
element** by value (the element that would be at position `k` from the end if the
array were sorted ascending; duplicates count toward the ranking).

## Constraints
- `1 <= k <= len(nums) <= 10^5`.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [3,2,1,5,6,4], k = 2`
Output: `5`

Input: `nums = [3,2,3,1,2,4,5,5,6], k = 4`
Output: `4`

Input: `nums = [1], k = 1`
Output: `1`
