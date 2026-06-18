A path is a sequence of nodes connected by edges, each used at most once; it need
not pass through the root. Given the level-order array `root` of a binary tree,
return **the maximum path sum over all non-empty paths**.

## Constraints
- `1 <= number of nodes <= 3 * 10^4`
- `-1000 <= Node.val <= 1000`

## Examples
Input: `root = [1,2,3]`
Output: `6`
Explanation: the path `2 -> 1 -> 3` sums to `6`.

![Example 2: best path 15 -> 20 -> 7](/problems/binary-tree-maximum-path-sum/assets/example-2.svg)

Input: `root = [-10,9,20,null,null,15,7]`
Output: `42`
Explanation: the path `15 -> 20 -> 7` sums to `42`.
