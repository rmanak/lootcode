def widthOfBinaryTree(root):
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
    q = deque([(0, 0)])
    best = 0
    while q:
        best = max(best, q[-1][1] - q[0][1] + 1)
        nxt = []
        for node, idx in q:
            if left.get(node) is not None:
                nxt.append((left[node], 2 * idx))
            if right.get(node) is not None:
                nxt.append((right[node], 2 * idx + 1))
        q = deque(nxt)
    return best
