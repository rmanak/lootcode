A rooted tree on nodes `1..n` had **one extra directed edge** added, producing
`edges` (with exactly `n` edges). Return the edge that can be removed so the result
is again a rooted tree. If several edges qualify, return the one that appears **last**
in `edges`.

## Constraints
- `3 <= len(edges) <= 1000`
- nodes are labeled `1..n`

## Examples
Input: `edges = [[1,2],[1,3],[2,3]]`
Output: `[2,3]`
Explanation: Node `3` has two parents; removing `[2,3]` restores a tree.

Input: `edges = [[1,2],[2,3],[3,1]]`
Output: `[3,1]`
Explanation: The edge `[3,1]` closes a directed cycle.
