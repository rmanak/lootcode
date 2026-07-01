> **Format:** your function works with `TreeNode` objects (`value`, `left`, `right`); `None` is an empty tree. Trees are shown below in LeetCode **level-order array** form (`null` = missing child; trailing `null`s dropped).

Flatten the binary tree (given as a `TreeNode`) into a "linked list" in
**preorder**: every node's left child becomes `null` and its right child is the next
node in preorder. Return the root of the flattened tree (a `TreeNode`) — a
right-leaning chain shown below like `[1,null,2,null,3,...]`.

## Constraints
- The number of nodes is in `[0, 2000]`.
- `-100 <= node value <= 100`

## Examples
Input: `root = [1,2,5,3,4,null,6]`
Output: `[1,null,2,null,3,null,4,null,5,null,6]`
Explanation: Preorder is `1,2,3,4,5,6`, laid out as a right-only chain.

Input: `root = []`
Output: `[]`
Explanation: An empty tree stays empty.
