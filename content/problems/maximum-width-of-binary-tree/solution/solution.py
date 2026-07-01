def widthOfBinaryTree(root):
    from collections import deque

    if root is None:
        return 0
    q = deque([(root, 0)])
    best = 0
    while q:
        best = max(best, q[-1][1] - q[0][1] + 1)
        nxt = []
        for node, idx in q:
            if node.left:
                nxt.append((node.left, 2 * idx))
            if node.right:
                nxt.append((node.right, 2 * idx + 1))
        q = deque(nxt)
    return best
