def pathSum(root, targetSum):
    if not root:
        return []
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    res = []

    def dfs(node, remaining, path):
        v = val[node]
        path.append(v)
        l, r = left.get(node), right.get(node)
        if l is None and r is None and remaining == v:
            res.append(path[:])
        else:
            if l is not None:
                dfs(l, remaining - v, path)
            if r is not None:
                dfs(r, remaining - v, path)
        path.pop()

    dfs(0, targetSum, [])
    return res
