Given two sorted arrays `nums1` and `nums2`, return **the median of all the
numbers combined**, as a floating-point value. If the combined count is even, the
median is the average of the two middle values.

## Constraints
- `0 <= len(nums1), len(nums2)`, and `1 <= len(nums1) + len(nums2) <= 2*10^5`.
- Each array is sorted ascending; `-10^6 <= values <= 10^6`.

## Examples
Input: `nums1 = [1,3], nums2 = [2]`
Output: `2.0`

Input: `nums1 = [1,2], nums2 = [3,4]`
Output: `2.5`

Input: `nums1 = [], nums2 = [1]`
Output: `1.0`
