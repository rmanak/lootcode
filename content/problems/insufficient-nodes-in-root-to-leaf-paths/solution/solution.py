def sufficientSubset(root, limit):
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

    def dfs(node, s):
        if node is None:
            return None
        s += val[node]
        if node not in left and node not in right:
            return node if s >= limit else None
        l = dfs(left.get(node), s)
        r = dfs(right.get(node), s)
        if l is None:
            left.pop(node, None)
        if r is None:
            right.pop(node, None)
        if node not in left and node not in right:
            return None
        return node

    if dfs(0, 0) is None:
        return []
    out = [val[0]]; q = deque([0])
    while q:
        node = q.popleft()
        for ch in (left.get(node), right.get(node)):
            if ch is None:
                out.append(None)
            else:
                out.append(val[ch]); q.append(ch)
    while out and out[-1] is None:
        out.pop()
    return out
