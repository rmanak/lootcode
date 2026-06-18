def shortestAlternatingPaths(n, redEdges, blueEdges):
    from collections import deque, defaultdict
    red, blue = defaultdict(list), defaultdict(list)
    for u, v in redEdges:
        red[u].append(v)
    for u, v in blueEdges:
        blue[u].append(v)
    dist = [[-1, -1] for _ in range(n)]
    dist[0][0] = dist[0][1] = 0
    q = deque([(0, 0), (0, 1)])
    while q:
        node, last = q.popleft()
        nxt = 1 - last
        for v in (blue[node] if nxt == 1 else red[node]):
            if dist[v][nxt] == -1:
                dist[v][nxt] = dist[node][last] + 1
                q.append((v, nxt))
    res = []
    for a, b in dist:
        if a == -1 and b == -1:
            res.append(-1)
        elif a == -1:
            res.append(b)
        elif b == -1:
            res.append(a)
        else:
            res.append(min(a, b))
    return res
