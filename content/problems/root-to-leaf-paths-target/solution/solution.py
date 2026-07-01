def pathSum(root, targetSum):
    res = []
    path = []

    def dfs(n, rem):
        if n is None:
            return
        path.append(n.value)
        rem -= n.value
        if n.left is None and n.right is None and rem == 0:
            res.append(list(path))
        dfs(n.left, rem)
        dfs(n.right, rem)
        path.pop()

    dfs(root, targetSum)
    return res
