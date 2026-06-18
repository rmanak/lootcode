def lcaDeepestLeaves(root):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0])
    nid, i, n = 1, 1, len(root)
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

    def dfs(node):
        if node is None:
            return (0, None)
        dl, ln = dfs(left.get(node))
        dr, rn = dfs(right.get(node))
        if dl == dr:
            return (dl + 1, node)
        if dl > dr:
            return (dl + 1, ln)
        return (dr + 1, rn)

    return val[dfs(0)[1]]
