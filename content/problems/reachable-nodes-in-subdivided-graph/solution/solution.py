def reachableNodes(edges, maxMoves, n):
    import heapq
    graph = [dict() for _ in range(n)]
    for u, v, cnt in edges:
        graph[u][v] = cnt
        graph[v][u] = cnt
    seen = {}                     # node -> max moves left when first settled
    pq = [(-maxMoves, 0)]
    while pq:
        ml, node = heapq.heappop(pq)
        ml = -ml
        if node in seen:
            continue
        seen[node] = ml
        for nei, cnt in graph[node].items():
            rem = ml - cnt - 1
            if nei not in seen and rem >= 0:
                heapq.heappush(pq, (-rem, nei))
    result = len(seen)
    for u, v, cnt in edges:
        a = min(cnt, seen.get(u, 0))
        b = min(cnt, seen.get(v, 0))
        result += min(cnt, a + b)
    return result
