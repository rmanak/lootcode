def invertTree(root):
    if root is None:
        return None
    root.left, root.right = invertTree(root.right), invertTree(root.left)
    return root
