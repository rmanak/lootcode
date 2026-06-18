def maxAncestorDiff(root):
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
    best = [0]

    def dfs(node, lo, hi):
        if node is None:
            return
        v = val[node]
        if abs(v - lo) > best[0]:
            best[0] = abs(v - lo)
        if abs(v - hi) > best[0]:
            best[0] = abs(v - hi)
        lo = min(lo, v); hi = max(hi, v)
        dfs(left.get(node), lo, hi)
        dfs(right.get(node), lo, hi)

    dfs(0, val[0], val[0])
    return best[0]
