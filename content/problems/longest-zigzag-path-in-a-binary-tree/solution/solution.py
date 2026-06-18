def longestZigZag(root):
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
    best = [0]

    def dfs(node):
        if node is None:
            return (-1, -1)
        ll = dfs(left.get(node))
        rr = dfs(right.get(node))
        dl = ll[1] + 1   # go left, then continue with the child's right length
        dr = rr[0] + 1   # go right, then continue with the child's left length
        best[0] = max(best[0], dl, dr)
        return (dl, dr)

    dfs(0)
    return best[0]
