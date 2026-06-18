def findTheCity(n, edges, distanceThreshold):
    INF = float("inf")
    dist = [[INF] * n for _ in range(n)]
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in edges:
        dist[u][v] = min(dist[u][v], w)
        dist[v][u] = min(dist[v][u], w)
    for k in range(n):
        dk = dist[k]
        for i in range(n):
            dik = dist[i][k]
            if dik == INF:
                continue
            di = dist[i]
            for j in range(n):
                nd = dik + dk[j]
                if nd < di[j]:
                    di[j] = nd
    best_city, best_count = -1, n + 1
    for i in range(n):
        c = sum(1 for j in range(n) if j != i and dist[i][j] <= distanceThreshold)
        if c <= best_count:
            best_count, best_city = c, i
    return best_city
