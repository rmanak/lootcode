def longestZigZag(root):
    best = [0]

    def dfs(node):
        if node is None:
            return (-1, -1)
        ll = dfs(node.left)
        rr = dfs(node.right)
        dl = ll[1] + 1   # step left, then continue with the child's right run
        dr = rr[0] + 1   # step right, then continue with the child's left run
        best[0] = max(best[0], dl, dr)
        return (dl, dr)

    dfs(root)
    return best[0]
