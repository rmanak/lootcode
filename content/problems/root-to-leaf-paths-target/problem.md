Return **all root-to-leaf paths** in the binary tree (level-order array) whose node
values sum to `targetSum`. Each path is the list of values from root to leaf; the
paths may be returned in any order.

## Constraints
- The number of nodes is in `[0, 5000]`.
- `-1000 <= node value, targetSum <= 1000`

## Examples
Input: `root = [5,4,8,11,null,13,4,7,2,null,null,5,1], targetSum = 22`
Output: `[[5,4,11,2],[5,8,4,5]]`
Explanation: Two root-to-leaf paths sum to `22`.

Input: `root = [1,2,3], targetSum = 4`
Output: `[[1,3]]`
Explanation: Only `1 -> 3` sums to `4`.
