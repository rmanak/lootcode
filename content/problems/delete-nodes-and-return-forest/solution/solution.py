def delNodes(root, to_delete):
    from collections import deque

    todel = set(to_delete)
    roots = []

    def dfs(node, is_root):
        if node is None:
            return None
        deleted = node.value in todel
        if is_root and not deleted:
            roots.append(node)
        node.left = dfs(node.left, deleted)
        node.right = dfs(node.right, deleted)
        return None if deleted else node

    dfs(root, True)

    def serialize(n):
        out, q = [], deque([n])
        while q:
            cur = q.popleft()
            if cur is None:
                out.append(None)
                continue
            out.append(cur.value)
            q.append(cur.left)
            q.append(cur.right)
        while out and out[-1] is None:
            out.pop()
        return out

    return [serialize(r) for r in roots]
