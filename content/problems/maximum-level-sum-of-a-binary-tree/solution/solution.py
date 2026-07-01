def maxLevelSum(root):
    from collections import deque

    best_level, best_sum, level = 1, None, 1
    q = deque([root]) if root else deque()
    while q:
        s = 0
        for _ in range(len(q)):
            node = q.popleft()
            s += node.value
            if node.left:
                q.append(node.left)
            if node.right:
                q.append(node.right)
        if best_sum is None or s > best_sum:
            best_sum, best_level = s, level
        level += 1
    return best_level
