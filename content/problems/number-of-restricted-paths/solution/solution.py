def countRestrictedPaths(n, edges):
    import heapq
    from collections import defaultdict
    MOD = 10 ** 9 + 7
    adj = defaultdict(list)
    for u, v, w in edges:
        adj[u].append((v, w))
        adj[v].append((u, w))
    dist = [float('inf')] * (n + 1)
    dist[n] = 0
    heap = [(0, n)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, w in adj[u]:
            if d + w < dist[v]:
                dist[v] = d + w
                heapq.heappush(heap, (dist[v], v))
    dp = [0] * (n + 1)
    dp[n] = 1
    for u in sorted(range(1, n + 1), key=lambda x: dist[x]):
        if u == n:
            continue
        dp[u] = sum(dp[v] for v, w in adj[u] if dist[v] < dist[u]) % MOD
    return dp[1] % MOD
