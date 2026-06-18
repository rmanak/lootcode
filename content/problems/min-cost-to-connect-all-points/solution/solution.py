def minCostConnectPoints(points):
    import heapq
    n = len(points)
    if n <= 1:
        return 0
    in_tree = [False] * n
    dist = [float('inf')] * n
    dist[0] = 0
    total = 0
    heap = [(0, 0)]
    cnt = 0
    while heap and cnt < n:
        d, u = heapq.heappop(heap)
        if in_tree[u]:
            continue
        in_tree[u] = True; total += d; cnt += 1
        ux, uy = points[u]
        for v in range(n):
            if not in_tree[v]:
                w = abs(ux - points[v][0]) + abs(uy - points[v][1])
                if w < dist[v]:
                    dist[v] = w; heapq.heappush(heap, (w, v))
    return total
