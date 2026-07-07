def connect(root):
    from collections import deque
    if root is None:
        return []
    res, q = [], deque([root])
    while q:
        for _ in range(len(q)):
            node = q.popleft()
            res.append(node.value)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(None)
    return res
