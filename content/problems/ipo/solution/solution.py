def findMaximizedCapital(k, w, profits, capital):
    import heapq
    projects = sorted(zip(capital, profits))
    heap = []
    i, n = 0, len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(heap, -projects[i][1])
            i += 1
        if not heap:
            break
        w += -heapq.heappop(heap)
    return w
