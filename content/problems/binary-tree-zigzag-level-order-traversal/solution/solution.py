def zigzagLevelOrder(root):
    from collections import deque
    if not root or root[0] is None:
        return []
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
    res, level, ltr = [], [0], True
    while level:
        row = [val[x] for x in level]
        res.append(row if ltr else row[::-1])
        nxt = []
        for x in level:
            if x in left:
                nxt.append(left[x])
            if x in right:
                nxt.append(right[x])
        level, ltr = nxt, not ltr
    return res
