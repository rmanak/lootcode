def minRefuelStops(target, startFuel, stations):
    import heapq
    heap = []
    fuel = startFuel
    stops = 0
    i = 0
    n = len(stations)
    while fuel < target:
        while i < n and stations[i][0] <= fuel:
            heapq.heappush(heap, -stations[i][1])
            i += 1
        if not heap:
            return -1
        fuel += -heapq.heappop(heap)
        stops += 1
    return stops
