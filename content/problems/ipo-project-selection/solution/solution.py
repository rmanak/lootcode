def findMaximizedCapital(k, w, profits, capital):
    import heapq
    projects = sorted(zip(capital, profits))
    available = []
    i = 0
    n = len(projects)
    for _ in range(k):
        while i < n and projects[i][0] <= w:
            heapq.heappush(available, -projects[i][1])
            i += 1
        if not available:
            break
        w += -heapq.heappop(available)
    return w
