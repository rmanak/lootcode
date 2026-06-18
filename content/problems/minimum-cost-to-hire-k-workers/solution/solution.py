def mincostToHireWorkers(quality, wage, K):
    import heapq
    workers = sorted((w / q, q) for w, q in zip(wage, quality))
    heap = []
    sumq = 0
    best = float('inf')
    for ratio, q in workers:
        heapq.heappush(heap, -q)
        sumq += q
        if len(heap) > K:
            sumq += heapq.heappop(heap)
        if len(heap) == K:
            best = min(best, ratio * sumq)
    return round(best, 5)
