def largestValues(root):
    from collections import deque

    if root is None:
        return []
    res = []
    q = deque([root])
    while q:
        best = None
        for _ in range(len(q)):
            node = q.popleft()
            best = node.value if best is None else max(best, node.value)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(best)
    return res
