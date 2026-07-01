def diameterOfBinaryTree(root):
    best = [0]

    def height(n):
        if n is None:
            return 0
        lh = height(n.left)
        rh = height(n.right)
        best[0] = max(best[0], lh + rh)
        return 1 + max(lh, rh)

    height(root)
    return best[0]
