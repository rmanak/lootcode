def levelOrder(root):
    from collections import deque

    if root is None:
        return []
    q, res = deque([root]), []
    while q:
        level = []
        for _ in range(len(q)):
            cur = q.popleft()
            level.append(cur.value)
            if cur.left:
                q.append(cur.left)
            if cur.right:
                q.append(cur.right)
        res.append(level)
    return res
