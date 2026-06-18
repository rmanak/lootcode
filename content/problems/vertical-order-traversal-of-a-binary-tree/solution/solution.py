def verticalTraversal(root):
    from collections import deque, defaultdict
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
    nodes = []

    def dfs(node, x, y):
        if node is None:
            return
        nodes.append((x, y, val[node]))
        dfs(left.get(node), x - 1, y + 1)
        dfs(right.get(node), x + 1, y + 1)

    dfs(0, 0, 0)
    cols = defaultdict(list)
    for x, y, v in nodes:
        cols[x].append((y, v))
    return [[v for _, v in sorted(cols[x], key=lambda t: (t[0], t[1]))] for x in sorted(cols)]
