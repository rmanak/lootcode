def getSkyline(buildings):
    import heapq
    events = []
    for left, right, height in buildings:
        events.append((left, -height, right))
        events.append((right, 0, 0))
    events.sort()
    res = []
    live = [(0, float("inf"))]
    for x, neg_h, right in events:
        while live[0][1] <= x:
            heapq.heappop(live)
        if neg_h:
            heapq.heappush(live, (neg_h, right))
        cur = -live[0][0]
        if not res or res[-1][1] != cur:
            res.append([x, cur])
    return res
