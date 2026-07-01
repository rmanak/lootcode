def zigzagLevelOrder(root):
    from collections import deque

    if root is None:
        return []
    res, q, ltr = [], deque([root]), True
    while q:
        row = []
        for _ in range(len(q)):
            node = q.popleft()
            row.append(node.value)
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        res.append(row if ltr else row[::-1])
        ltr = not ltr
    return res
