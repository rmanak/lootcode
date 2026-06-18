Choose exactly `k` indices. The score is `(sum of the chosen nums1) * (minimum of the
chosen nums2)`. Return the **maximum possible score**.

## Constraints
- `1 <= len(nums1) == len(nums2) <= 10^5`
- `1 <= k <= len(nums1)`
- `0 <= nums1[i] <= 10^5`, `1 <= nums2[i] <= 10^5`

## Examples
Input: `nums1 = [1,3,3,2], nums2 = [2,1,3,4], k = 3`
Output: `12`
Explanation: Indices with nums1 sum 6 and nums2 minimum 2 give 12.

Input: `nums1 = [4,2,3,1,1], nums2 = [7,5,10,9,6], k = 1`
Output: `30`
Explanation: Index 2 gives `3 * 10 = 30`.
