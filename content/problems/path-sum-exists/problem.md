Return `true` if the binary tree (level-order array) has a **root-to-leaf** path
whose node values sum to exactly `targetSum`.

## Constraints
- The number of nodes is in `[0, 5000]`.
- `-1000 <= node value, targetSum <= 1000`

## Examples
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,null,1], targetSum = 22`
Output: `true`
Explanation: The path `5 -> 4 -> 11 -> 2` sums to `22`.

Input: `root = [1,2,3], targetSum = 5`
Output: `false`
Explanation: Root-to-leaf sums are `3` and `4`, never `5`.
