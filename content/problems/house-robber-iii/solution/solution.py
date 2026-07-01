def rob(root):
    def dfs(node):
        if node is None:
            return (0, 0)
        l = dfs(node.left)
        r = dfs(node.right)
        rob_this = node.value + l[1] + r[1]
        skip = max(l) + max(r)
        return (rob_this, skip)

    return max(dfs(root))
