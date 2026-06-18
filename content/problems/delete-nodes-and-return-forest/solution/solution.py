def delNodes(root, to_delete):
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
    todel = set(to_delete)
    roots = []

    def dfs(node, is_root):
        if node is None:
            return None
        deleted = val[node] in todel
        if is_root and not deleted:
            roots.append(node)
        l = dfs(left.get(node), deleted)
        r = dfs(right.get(node), deleted)
        if l is None:
            left.pop(node, None)
        else:
            left[node] = l
        if r is None:
            right.pop(node, None)
        else:
            right[node] = r
        return None if deleted else node

    dfs(0, True)

    def serialize(rid):
        out = [val[rid]]; q2 = deque([rid])
        while q2:
            node = q2.popleft()
            for ch in (left.get(node), right.get(node)):
                if ch is None:
                    out.append(None)
                else:
                    out.append(val[ch]); q2.append(ch)
        while out and out[-1] is None:
            out.pop()
        return out

    return [serialize(rid) for rid in roots]
