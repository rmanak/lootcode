> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given a binary tree as a level-order array (`null` marks a missing child), imagine
standing on the right side. Return the values of the nodes visible from top to
bottom — the **rightmost node at each depth**.

## Constraints
- The number of nodes is in `[0, 100]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,3,null,5,null,4]`
Output: `[1,3,4]`
Explanation: From the right you see `1`, then `3`, then `4`.

Input: `root = [1,null,3]`
Output: `[1,3]`
Explanation: Only the right spine is visible.
