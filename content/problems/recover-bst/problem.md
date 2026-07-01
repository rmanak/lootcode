> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Exactly two nodes of a binary search tree (given as a `TreeNode`) had their
values swapped by mistake. Recover the tree without changing its structure and
return its root (a `TreeNode`) with the values corrected.

## Constraints
- The number of nodes is in `[2, 1000]`.
- All node values are distinct; exactly two were swapped.

## Examples
Input: `root = [1,3,null,null,2]`
Output: `[3,1,null,null,2]`
Explanation: Swapping `1` and `3` restores the BST ordering.

Input: `root = [3,1,4,null,null,2]`
Output: `[2,1,4,null,null,3]`
Explanation: Nodes `3` and `2` were swapped; swapping them back restores the BST.
