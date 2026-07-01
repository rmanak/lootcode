def maxAncestorDiff(root):
    best = [0]

    def dfs(node, lo, hi):
        if node is None:
            return
        v = node.value
        best[0] = max(best[0], abs(v - lo), abs(v - hi))
        lo, hi = min(lo, v), max(hi, v)
        dfs(node.left, lo, hi)
        dfs(node.right, lo, hi)

    if root is not None:
        dfs(root, root.value, root.value)
    return best[0]
