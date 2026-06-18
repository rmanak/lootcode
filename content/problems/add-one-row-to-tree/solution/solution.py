def addOneRow(root, v, d):
    from collections import deque
    val = {0: root[0]}
    left, right = {}, {}
    q = deque([0]); nid, i, n = 1, 1, len(root)
    while q and i < n:
        cur = q.popleft()
        if i < n:
            x = root[i]; i += 1
            if x is not None:
                val[nid] = x; left[cur] = nid; q.append(nid); nid += 1
        if i < n:
            x = root[i]; i += 1
            if x is not None:
                val[nid] = x; right[cur] = nid; q.append(nid); nid += 1
    counter = [max(val) + 1]

    def fresh(value):
        node = counter[0]; counter[0] += 1; val[node] = value
        return node

    if d == 1:
        nr = fresh(v); left[nr] = 0
        rootid = nr
    else:
        level = [0]; depth = 1
        while depth < d - 1:
            nxt = []
            for x in level:
                if left.get(x) is not None:
                    nxt.append(left[x])
                if right.get(x) is not None:
                    nxt.append(right[x])
            level = nxt; depth += 1
        for x in level:
            old_l, old_r = left.get(x), right.get(x)
            nl = fresh(v); nrr = fresh(v)
            left[x] = nl; right[x] = nrr
            if old_l is not None:
                left[nl] = old_l
            if old_r is not None:
                right[nrr] = old_r
        rootid = 0
    out = [val[rootid]]; q = deque([rootid])
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
