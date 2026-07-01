def deepestLeavesSum(root):
    from collections import deque

    q = deque([root]) if root else deque()
    s = 0
    while q:
        s = 0
        for _ in range(len(q)):
            node = q.popleft()
            s += node.value
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
    return s
