def rightSideView(root):
    from collections import deque

    if root is None:
        return []
    res = []
    q = deque([root])
    while q:
        n = len(q)
        for i in range(n):
            node = q.popleft()
            if i == n - 1:
                res.append(node.value)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return res
