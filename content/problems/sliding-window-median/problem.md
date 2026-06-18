Given an integer array `nums` and an **odd** window size `k`, return an array of the
medians of every contiguous window of size `k`, left to right. (With odd `k` each
median is the middle value of the sorted window.)

## Constraints
- `1 <= k <= len(nums) <= 10^5`
- `k` is odd
- `-10^9 <= nums[i] <= 10^9`

## Examples
Input: `nums = [1,3,-1,-3,5,3,6,7], k = 3`
Output: `[1,-1,-1,3,5,6]`
Explanation: Each window's middle value after sorting.

Input: `nums = [1,2], k = 1`
Output: `[1,2]`
Explanation: A window of size `1` has the element itself as its median.
