def frogPosition(n, edges, t, target):
    from collections import defaultdict, deque
    if n == 1:
        return 1.0 if target == 1 else 0.0
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    visited = {1}
    dq = deque([(1, 1.0, 0)])
    while dq:
        node, prob, time = dq.popleft()
        children = [c for c in adj[node] if c not in visited]
        if node == target:
            if time == t or not children:
                return round(prob, 5)
            return 0.0
        if time == t:
            continue
        for c in children:
            visited.add(c)
            dq.append((c, prob / len(children), time + 1))
    return 0.0
