def btreeGameWinningMove(root, n, x):
    def find(node):
        if node is None:
            return None
        if node.value == x:
            return node
        return find(node.left) or find(node.right)

    def size(node):
        if node is None:
            return 0
        return 1 + size(node.left) + size(node.right)

    target = find(root)
    lsz = size(target.left)
    rsz = size(target.right)
    psz = n - 1 - lsz - rsz
    return max(lsz, rsz, psz) > n // 2
