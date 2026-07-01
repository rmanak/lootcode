def addOneRow(root, v, d):
    if d == 1:
        return TreeNode(v, root, None)

    def dfs(node, depth):
        if node is None:
            return
        if depth == d - 1:
            node.left = TreeNode(v, node.left, None)
            node.right = TreeNode(v, None, node.right)
            return
        dfs(node.left, depth + 1)
        dfs(node.right, depth + 1)

    dfs(root, 1)
    return root
