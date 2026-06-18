A node `X` is **good** if no node on the path from the root down to `X` has a value
greater than `X` (the root is always good). Return the number of good nodes in the
binary tree (given as a level-order array, `null` = missing child).

## Constraints
- The number of nodes is in `[1, 10^5]`.
- `-10^4 <= node value <= 10^4`

## Examples
Input: `root = [3,1,4,3,null,1,5]`
Output: `4`
Explanation: The good nodes are `3` (root), `4`, `5`, and the deeper `3`.

Input: `root = [3,3,null,4,2]`
Output: `3`
Explanation: `3` (root), the child `3`, and `4` are good.
