def maxProbability(n, edges, succProb, start, end):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    for (u, v), p in zip(edges, succProb):
        adj[u].append((v, p))
        adj[v].append((u, p))
    prob = [0.0] * n
    prob[start] = 1.0
    heap = [(-1.0, start)]
    while heap:
        negp, u = heapq.heappop(heap)
        p = -negp
        if u == end:
            return round(p, 5)
        if p < prob[u]:
            continue
        for v, w in adj[u]:
            if p * w > prob[v]:
                prob[v] = p * w
                heapq.heappush(heap, (-prob[v], v))
    return round(prob[end], 5)
