def lcaDeepestLeaves(root):
    def dfs(node):
        if node is None:
            return (0, None)
        dl, ln = dfs(node.left)
        dr, rn = dfs(node.right)
        if dl == dr:
            return (dl + 1, node)
        return (dl + 1, ln) if dl > dr else (dr + 1, rn)

    return dfs(root)[1].value
