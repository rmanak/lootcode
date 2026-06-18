def minimumDeviation(nums):
    import heapq
    heap, mn = [], float("inf")
    for x in nums:
        if x % 2 == 1:
            x *= 2
        heap.append(-x)
        mn = min(mn, x)
    heapq.heapify(heap)
    best = float("inf")
    while True:
        mx = -heapq.heappop(heap)
        best = min(best, mx - mn)
        if mx % 2 == 1:
            break
        mx //= 2
        mn = min(mn, mx)
        heapq.heappush(heap, -mx)
    return best
