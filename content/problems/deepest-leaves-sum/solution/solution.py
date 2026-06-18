def deepestLeavesSum(root):
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
    q = deque([0])
    s = 0
    while q:
        s = sum(val[x] for x in q)
        nxt = []
        for x in q:
            if left.get(x) is not None:
                nxt.append(left[x])
            if right.get(x) is not None:
                nxt.append(right[x])
        q = deque(nxt)
    return s
