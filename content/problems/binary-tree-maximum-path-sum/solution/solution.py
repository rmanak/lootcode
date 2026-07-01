def maxPathSum(root):
    best = [float("-inf")]

    def gain(n):
        if n is None:
            return 0
        left = max(gain(n.left), 0)
        right = max(gain(n.right), 0)
        best[0] = max(best[0], n.value + left + right)
        return n.value + max(left, right)

    gain(root)
    return best[0]
