def pruneTree(root):
    if root is None:
        return None
    root.left = pruneTree(root.left)
    root.right = pruneTree(root.right)
    if root.value == 0 and root.left is None and root.right is None:
        return None
    return root
