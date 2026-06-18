Given a sorted array of distinct integers `nums` and a `target`, return **the
index where `target` is found**, or **the index where it should be inserted** to
keep the array sorted. Aim for `O(log n)`.

## Constraints
- `0 <= len(nums) <= 10^5`, sorted ascending with distinct values.
- `-10^9 <= nums[i], target <= 10^9`.

## Examples
Input: `nums = [1,3,5,6], target = 5`
Output: `2`

Input: `nums = [1,3,5,6], target = 2`
Output: `1`

Input: `nums = [1,3,5,6], target = 7`
Output: `4`
