def findFrequentTreeSum(root):
    from collections import deque, Counter
    if not root:
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
    counts = Counter()

    def dfs(node):
        s = val[node]
        for ch in (left.get(node), right.get(node)):
            if ch is not None:
                s += dfs(ch)
        counts[s] += 1
        return s

    dfs(0)
    mx = max(counts.values())
    return [s for s, c in counts.items() if c == mx]
