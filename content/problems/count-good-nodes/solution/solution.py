def goodNodes(root):
    def dfs(node, mx):
        if node is None:
            return 0
        good = 1 if node.value >= mx else 0
        nm = max(mx, node.value)
        return good + dfs(node.left, nm) + dfs(node.right, nm)

    return dfs(root, float("-inf"))
