def getMinimumDifference(root):
    vals = []
    def ino(n):
        if n is None:
            return
        ino(n.left)
        vals.append(n.value)
        ino(n.right)
    ino(root)
    return min(vals[i + 1] - vals[i] for i in range(len(vals) - 1))
