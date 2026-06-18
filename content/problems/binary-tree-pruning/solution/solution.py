def pruneTree(root):
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

    def keep(node):
        if node is None:
            return False
        kl = keep(left.get(node))
        kr = keep(right.get(node))
        if not kl:
            left.pop(node, None)
        if not kr:
            right.pop(node, None)
        return val[node] == 1 or kl or kr

    if not keep(0):
        return []
    out = [val[0]]
    q = deque([0])
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
