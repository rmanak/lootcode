def pathSum(root, targetSum):
    res = []

    def dfs(node, remaining, path):
        if node is None:
            return
        v = node.value
        path.append(v)
        if node.left is None and node.right is None and remaining == v:
            res.append(path[:])
        else:
            dfs(node.left, remaining - v, path)
            dfs(node.right, remaining - v, path)
        path.pop()

    dfs(root, targetSum, [])
    return res
