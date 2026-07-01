> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given a **complete** binary tree as a level-order array (every level full except
possibly the last, which is filled left to right), return the number of nodes.

## Constraints
- The number of nodes is in `[0, 5*10^4]`.
- The tree is complete.

## Examples
Input: `root = [1,2,3,4,5,6]`
Output: `6`
Explanation: All six positions hold a node.

Input: `root = [1]`
Output: `1`
Explanation: A single root node.
