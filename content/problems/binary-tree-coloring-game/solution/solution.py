def btreeGameWinningMove(root, n, x):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, m = 1, 1, len(root)
    while q and i < m:
        cur = q.popleft()
        if i < m:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; left[cur] = nid; q.append(nid); nid += 1
        if i < m:
            v = root[i]; i += 1
            if v is not None:
                val[nid] = v; right[cur] = nid; q.append(nid); nid += 1
    target = next(nd for nd in val if val[nd] == x)

    def size(node):
        if node is None:
            return 0
        return 1 + size(left.get(node)) + size(right.get(node))

    lsz = size(left.get(target))
    rsz = size(right.get(target))
    psz = n - 1 - lsz - rsz
    return max(lsz, rsz, psz) > n // 2
