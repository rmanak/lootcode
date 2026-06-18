def largestValues(root):
    if not root:
        return []
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
    res = []
    level = [0]
    while level:
        res.append(max(val[x] for x in level))
        nxt = []
        for x in level:
            if x in left:
                nxt.append(left[x])
            if x in right:
                nxt.append(right[x])
        level = nxt
    return res
