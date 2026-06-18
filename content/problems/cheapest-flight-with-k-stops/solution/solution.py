def findCheapestPrice(n, flights, src, dst, k):
    inf = float("inf")
    dist = [inf] * n
    dist[src] = 0
    for _ in range(k + 1):
        nd = dist[:]
        for u, v, w in flights:
            if dist[u] + w < nd[v]:
                nd[v] = dist[u] + w
        dist = nd
    return -1 if dist[dst] == inf else dist[dst]
