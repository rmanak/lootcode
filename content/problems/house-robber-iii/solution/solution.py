def rob(root):
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

    def dfs(node):
        if node is None:
            return (0, 0)
        l = dfs(left.get(node))
        r = dfs(right.get(node))
        rob_this = val[node] + l[1] + r[1]
        skip = max(l) + max(r)
        return (rob_this, skip)

    return max(dfs(0))
