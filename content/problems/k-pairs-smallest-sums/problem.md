Given two ascending arrays `nums1` and `nums2` and an integer `k`, return the `k`
pairs `[a, b]` (one value from each array) with the smallest sums `a + b`. Return
them **ordered by increasing sum**, breaking ties by the smaller first value and
then the smaller second value. If fewer than `k` pairs exist, return all of them.

## Constraints
- `1 <= len(nums1), len(nums2) <= 10^4`
- `-10^9 <= nums1[i], nums2[i] <= 10^9`
- `1 <= k <= 1000`

## Examples
Input: `nums1 = [1,7,11], nums2 = [2,4,6], k = 3`
Output: `[[1,2],[1,4],[1,6]]`
Explanation: The three smallest sums all pair `1` from `nums1`.

Input: `nums1 = [1,1,2], nums2 = [1,2,3], k = 2`
Output: `[[1,1],[1,1]]`
Explanation: Both smallest pairs sum to `2`.
