def findBottomLeftValue(root):
    from collections import deque

    q = deque([root])
    leftmost = root.value
    while q:
        leftmost = q[0].value
        for _ in range(len(q)):
            node = q.popleft()
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return leftmost
