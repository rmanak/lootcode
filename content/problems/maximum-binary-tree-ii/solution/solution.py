def insertIntoMaxTree(root, val):
    if root is None or val > root.value:
        return TreeNode(val, root, None)
    root.right = insertIntoMaxTree(root.right, val)
    return root
