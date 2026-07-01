> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Return `true` if the binary tree (level-order array) is a **mirror image of itself**
around its center.

## Constraints
- The number of nodes is in `[0, 1000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,2,3,4,4,3]`
Output: `true`
Explanation: The left and right subtrees mirror each other.

Input: `root = [1,2,2,null,3,null,3]`
Output: `false`
Explanation: The two `3`s sit on the same side, breaking the mirror.
