> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary tree (`null`/`None` marks a missing
child), return **`true` if it is a valid binary search tree**: every node's left
subtree holds only smaller keys, its right subtree only larger keys, and both
subtrees are themselves valid BSTs.

## Constraints
- `1 <= number of nodes <= 10^4`
- `-2^31 <= node.valueue <= 2^31 - 1`

## Examples
Input: `root = [2,1,3]`
Output: `true`

Input: `root = [5,1,4,null,null,3,6]`
Output: `false`
Explanation: the right child `4` is smaller than the root `5`.
