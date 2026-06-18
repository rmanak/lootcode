Every value in the integer array `nums` appears exactly twice except for one
value that appears once. Return **the value that appears only once**.

Aim for `O(n)` time and `O(1)` extra space.

## Constraints
- `1 <= len(nums) <= 3*10^4` and `len(nums)` is odd.
- Exactly one element appears once; every other element appears exactly twice.
- `-10^9 <= nums[i] <= 10^9`.

## Examples
Input: `nums = [2,2,1]`
Output: `1`

Input: `nums = [4,1,2,1,2]`
Output: `4`

Input: `nums = [7]`
Output: `7`
