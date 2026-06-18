Given `nums` sorted in non-decreasing order, build a **height-balanced** binary
search tree and return it as a level-order array. When a range has an even number of
elements, take the **left** of the two middle elements as the subtree root (so the
answer is unique).

## Constraints
- `1 <= len(nums) <= 10^4`
- `nums` is sorted in non-decreasing order.

## Examples
Input: `nums = [-10,-3,0,5,9]`
Output: `[0,-10,5,null,-3,null,9]`
Explanation: `0` is the middle root; each half is built recursively.

Input: `nums = [1,3]`
Output: `[1,null,3]`
Explanation: With two elements the left one (`1`) is the root.
