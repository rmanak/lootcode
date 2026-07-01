def sufficientSubset(root, limit):
    def dfs(node, s):
        if node is None:
            return None
        s += node.value
        if node.left is None and node.right is None:
            return node if s >= limit else None
        node.left = dfs(node.left, s)
        node.right = dfs(node.right, s)
        if node.left is None and node.right is None:
            return None
        return node

    return dfs(root, 0)
