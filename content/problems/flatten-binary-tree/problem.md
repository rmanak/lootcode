Flatten the binary tree (given as a level-order array) into a "linked list" in
**preorder**: every node's left child becomes `null` and its right child is the next
node in preorder. Return the resulting tree as a level-order array (a right-leaning
chain like `[1,null,2,null,3,...]`).

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
