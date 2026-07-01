> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary search tree and two values `p` and
`q` present in it, return **the value of their lowest common ancestor** — the
deepest node having both as descendants (a node may be a descendant of itself).

## Constraints
- `2 <= number of nodes <= 10^5`
- `-10^9 <= node.valueue <= 10^9`; all values unique
- `p != q`; both `p` and `q` exist in the tree

## Examples
Input: `root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8`
Output: `6`

Input: `root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 4`
Output: `2`
Explanation: a node can be a descendant of itself.

Input: `root = [2,1], p = 2, q = 1`
Output: `2`
