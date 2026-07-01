def widthOfBinaryTree(root):
    from collections import deque

    if root is None:
        return 0
    maxw = 0
    q = deque([(root, 0)])
    while q:
        n = len(q)
        first = q[0][1]
        last = 0
        for _ in range(n):
            node, idx = q.popleft()
            idx -= first
            last = idx
            if node.left:
                q.append((node.left, 2 * idx))
            if node.right:
                q.append((node.right, 2 * idx + 1))
        maxw = max(maxw, last + 1)
    return maxw
