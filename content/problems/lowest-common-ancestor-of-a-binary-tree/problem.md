> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary tree and two values `p` and `q`
present in it, return **the value of their lowest common ancestor** — the deepest
node having both as descendants (a node may be a descendant of itself).

## Constraints
- `2 <= number of nodes <= 10^5`
- `-10^9 <= node.valueue <= 10^9`; all values unique
- `p != q`; both `p` and `q` exist in the tree

## Examples
![Example 1: LCA of 5 and 1 is 3](/problems/lowest-common-ancestor-of-a-binary-tree/assets/example-1.svg)

Input: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 1`
Output: `3`

Input: `root = [3,5,1,6,2,0,8,null,null,7,4], p = 5, q = 4`
Output: `5`
Explanation: `4` is in the subtree of `5`, so `5` is its own ancestor here.

Input: `root = [1,2], p = 1, q = 2`
Output: `1`
