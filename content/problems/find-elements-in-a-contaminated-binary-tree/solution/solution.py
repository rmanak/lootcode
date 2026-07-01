def findElements(root, queries):
    from collections import deque

    present = set()
    if root is not None:
        root.value = 0
        present.add(0)
        q = deque([root])
        while q:
            node = q.popleft()
            x = node.value
            if node.left:
                node.left.value = 2 * x + 1
                present.add(node.left.value)
                q.append(node.left)
            if node.right:
                node.right.value = 2 * x + 2
                present.add(node.right.value)
                q.append(node.right)
    return [qv in present for qv in queries]
