def smallestRange(lists):
    import heapq
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(heap)
    cur_max = max(lst[0] for lst in lists)
    best = [heap[0][0], cur_max]
    while True:
        val, i, j = heapq.heappop(heap)
        size = cur_max - val
        if size < best[1] - best[0] or (size == best[1] - best[0] and val < best[0]):
            best = [val, cur_max]
        if j + 1 == len(lists[i]):
            break
        nxt = lists[i][j + 1]
        cur_max = max(cur_max, nxt)
        heapq.heappush(heap, (nxt, i, j + 1))
    return best
