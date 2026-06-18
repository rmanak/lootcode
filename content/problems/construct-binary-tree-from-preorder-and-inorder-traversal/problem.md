Given `preorder` and `inorder` traversals of a binary tree with **unique** values,
reconstruct the tree and **return its level-order array** (`null`/`None` marks a
missing child; trailing nulls are dropped).

## Constraints
- `1 <= len(preorder) <= 3000`, `len(inorder) == len(preorder)`
- `-3000 <= preorder[i], inorder[i] <= 3000`; all values unique
- `inorder` is a permutation of `preorder` consistent with some binary tree

## Examples
![Example 1: the reconstructed tree](/problems/construct-binary-tree-from-preorder-and-inorder-traversal/assets/example-1.svg)

Input: `preorder = [3,9,20,15,7], inorder = [9,3,15,20,7]`
Output: `[3,9,20,null,null,15,7]`

Input: `preorder = [-1], inorder = [-1]`
Output: `[-1]`
