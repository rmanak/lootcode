Given the level-order array `root` of a binary tree, invert it (mirror every
left/right pair) and **return the level-order array of the inverted tree**
(`null`/`None` marks a missing child; trailing nulls are dropped).

## Constraints
- `0 <= number of nodes <= 100`
- `-100 <= Node.val <= 100`

## Examples
![Example 1: mirroring every left/right pair](/problems/invert-binary-tree/assets/example-1.svg)

Input: `root = [4,2,7,1,3,6,9]`
Output: `[4,7,2,9,6,3,1]`

Input: `root = [2,1,3]`
Output: `[2,3,1]`

Input: `root = []`
Output: `[]`
