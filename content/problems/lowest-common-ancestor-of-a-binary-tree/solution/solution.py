def lowestCommonAncestor(root, p, q):
    def lca(n):
        if n is None or n.value == p or n.value == q:
            return n
        left = lca(n.left)
        right = lca(n.right)
        if left and right:
            return n
        return left or right

    return lca(root).value
