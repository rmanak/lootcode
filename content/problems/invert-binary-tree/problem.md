Given the `root` of a binary tree (a `TreeNode` with `value`, `left`, `right`),
invert it — mirror every left/right pair — and **return the root of the inverted
tree**.

Trees are shown below in LeetCode level-order array form (`null` marks a missing
child; trailing nulls are dropped), but your function receives and returns a
`TreeNode` (or `None` for an empty tree).

## Constraints
- `0 <= number of nodes <= 100`
- `-100 <= node.value <= 100`

## Examples
![Example 1: mirroring every left/right pair](/problems/invert-binary-tree/assets/example-1.svg)

Input: `root = [4,2,7,1,3,6,9]`
Output: `[4,7,2,9,6,3,1]`

Input: `root = [2,1,3]`
Output: `[2,3,1]`

Input: `root = []`
Output: `[]`
