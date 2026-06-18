The binary trees `root` and `subRoot` are given as level-order arrays, where `null`
marks a missing child (e.g. `[3,4,5,1,2]`). Return **`true` if some subtree of
`root` has exactly the same structure and node values as `subRoot`**, otherwise
`false`. A tree is a subtree of itself.

![Example 1: subRoot [4,1,2] matches a subtree of root [3,4,5,1,2]](/problems/subtree-of-another-tree/assets/example-1.svg)

## Constraints
- The number of nodes in `root` is in `[1, 2000]`; in `subRoot`, `[1, 1000]`.
- `-10^4 <= node value <= 10^4`

## Examples
Input: `root = [3,4,5,1,2], subRoot = [4,1,2]`
Output: `true`

![Example 2: subRoot [4,1,2] does not match — the candidate node 2 has an extra child](/problems/subtree-of-another-tree/assets/example-2.svg)

Input: `root = [3,4,5,1,2,null,null,null,null,0], subRoot = [4,1,2]`
Output: `false`
Explanation: The only `4`-rooted subtree has an extra node `0`, so it is not identical to `subRoot`.
