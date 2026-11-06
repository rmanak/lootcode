def averageOfLevels(root):
    from collections import deque
    res, q = [], deque([root] if root else [])
    while q:
        total, cnt = 0, len(q)
        for _ in range(cnt):
            node = q.popleft()
            total += node.value
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(round(total / cnt, 5))
    return res
