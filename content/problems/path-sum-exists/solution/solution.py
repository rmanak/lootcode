def hasPathSum(root, targetSum):
    def dfs(n, rem):
        if n is None:
            return False
        rem -= n.value
        if n.left is None and n.right is None:
            return rem == 0
        return dfs(n.left, rem) or dfs(n.right, rem)

    return dfs(root, targetSum) if root else False
