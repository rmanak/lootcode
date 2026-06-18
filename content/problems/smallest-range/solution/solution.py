def smallestRange(nums):
    import heapq
    heap = [(lst[0], i, 0) for i, lst in enumerate(nums)]
    heapq.heapify(heap)
    cur_max = max(lst[0] for lst in nums)
    best = [heap[0][0], cur_max]
    while True:
        mn, i, j = heapq.heappop(heap)
        if (cur_max - mn < best[1] - best[0] or
                (cur_max - mn == best[1] - best[0] and mn < best[0])):
            best = [mn, cur_max]
        if j + 1 == len(nums[i]):
            break
        nxt = nums[i][j + 1]
        cur_max = max(cur_max, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))
    return best
