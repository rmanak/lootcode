def sumOfDistancesInTree(n, edges):
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v in edges:
        adj[u].append(v); adj[v].append(u)
    count = [1] * n
    ans = [0] * n
    parent = [-1] * n
    visited = [False] * n
    order = []
    stack = [0]; visited[0] = True
    while stack:
        node = stack.pop(); order.append(node)
        for nb in adj[node]:
            if not visited[nb]:
                visited[nb] = True; parent[nb] = node; stack.append(nb)
    for node in reversed(order):
        p = parent[node]
        if p != -1:
            count[p] += count[node]
            ans[p] += ans[node] + count[node]
    for node in order[1:]:
        p = parent[node]
        ans[node] = ans[p] - count[node] + (n - count[node])
    return ans
