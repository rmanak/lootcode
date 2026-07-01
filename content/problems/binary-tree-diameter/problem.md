> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Given the `TreeNode` `root` of a binary tree, return **the diameter** — the
number of **edges** on the longest path between any two nodes (the path need not
pass through the root).

## Constraints
- `0 <= number of nodes <= 10^4`.
- `-100 <= node.valueue <= 100`; `null` marks an absent child.

## Examples
Input: `root = [1,2,3,4,5]`
Output: `3`
Explanation: the path `4 → 2 → 1 → 3` (or `5 → 2 → 1 → 3`) has 3 edges.

Input: `root = [1,2,3]`
Output: `2`

Input: `root = [1]`
Output: `0`
