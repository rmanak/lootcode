> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary tree, return **its level-order
traversal as a list of levels** — top to bottom, left to right within each level.

## Constraints
- `0 <= number of nodes <= 2000`
- `-1000 <= node.value <= 1000`

## Examples
Input: `root = [3,9,20,null,null,15,7]`
Output: `[[3],[9,20],[15,7]]`

Input: `root = [1]`
Output: `[[1]]`

Input: `root = []`
Output: `[]`
