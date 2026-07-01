def smallestFromLeaf(root):
    if root is None:
        return ""
    best = [None]

    def dfs(node, suffix):
        s = chr(97 + node.value) + suffix
        if node.left is None and node.right is None:
            if best[0] is None or s < best[0]:
                best[0] = s
            return
        if node.left is not None:
            dfs(node.left, s)
        if node.right is not None:
            dfs(node.right, s)

    dfs(root, "")
    return best[0]
