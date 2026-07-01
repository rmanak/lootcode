Given the roots `p` and `q` of two binary trees (each a `TreeNode` with `value`,
`left`, `right`, or `None`), return **`true` if the trees are identical** — same
shape and same node values.

Trees are shown below in LeetCode level-order array form (`null` marks a missing
child), but your function receives `p` and `q` as `TreeNode` objects (or `None`).

## Constraints
- `0 <= number of nodes in each tree <= 100`
- `-10^4 <= node.value <= 10^4`

## Examples
Input: `p = [1,2,3], q = [1,2,3]`
Output: `true`

Input: `p = [1,2], q = [1,null,2]`
Output: `false`

Input: `p = [1,2,1], q = [1,1,2]`
Output: `false`
