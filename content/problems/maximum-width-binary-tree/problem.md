> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

The **width** of a level is the distance between its leftmost and rightmost non-null
nodes, counting the null slots between them as if the tree were a full binary tree.
Return the **maximum width** across all levels of the binary tree (level-order
array).

## Constraints
- The number of nodes is in `[1, 3000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,3,2,5,3,null,9]`
Output: `4`
Explanation: The bottom level spans positions of `5` and `9` — width `4`.

Input: `root = [1,3,2,5]`
Output: `2`
Explanation: The level with `3` and `2` has width `2`.
