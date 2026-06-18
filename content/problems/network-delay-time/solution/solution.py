def networkDelayTime(times, n, k):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for u, v, w in times:
        adj[u].append((v, w))
    dist = {}
    heap = [(0, k)]
    while heap:
        d, u = heapq.heappop(heap)
        if u in dist:
            continue
        dist[u] = d
        for v, w in adj[u]:
            if v not in dist:
                heapq.heappush(heap, (d + w, v))
    if len(dist) < n:
        return -1
    return max(dist.values())
