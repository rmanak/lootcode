def validPath(n, edges, source, destination):
    if source == destination:
        return True
    from collections import deque, defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    seen = {source}
    q = deque([source])
    while q:
        node = q.popleft()
        if node == destination:
            return True
        for nb in adj[node]:
            if nb not in seen:
                seen.add(nb)
                q.append(nb)
    return False
