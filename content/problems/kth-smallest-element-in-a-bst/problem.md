> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary search tree and an integer `k`,
return **the `k`-th smallest value** (1-indexed) among all node values.

## Constraints
- `1 <= k <= n` where `n` is the number of nodes, `1 <= n <= 10^4`
- `0 <= node.valueue <= 10^4`

## Examples
Input: `root = [3,1,4,null,2], k = 1`
Output: `1`

Input: `root = [5,3,6,2,4,null,null,1], k = 3`
Output: `3`
