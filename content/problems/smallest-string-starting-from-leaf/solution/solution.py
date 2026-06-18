def smallestFromLeaf(root):
    if not root:
        return ""
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
    best = [None]

    def dfs(node, suffix):
        s = chr(97 + val[node]) + suffix
        l, rr = left.get(node), right.get(node)
        if l is None and rr is None:
            if best[0] is None or s < best[0]:
                best[0] = s
            return
        if l is not None:
            dfs(l, s)
        if rr is not None:
            dfs(rr, s)

    dfs(0, "")
    return best[0]
