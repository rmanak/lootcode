def maxPerformance(n, speed, efficiency, k):
    import heapq
    MOD = 10 ** 9 + 7
    engineers = sorted(zip(efficiency, speed), reverse=True)
    heap = []
    sum_speed = 0
    best = 0
    for eff, spd in engineers:
        heapq.heappush(heap, spd)
        sum_speed += spd
        if len(heap) > k:
            sum_speed -= heapq.heappop(heap)
        best = max(best, sum_speed * eff)
    return best % MOD
