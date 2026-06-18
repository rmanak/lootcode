import heapq
def mergeKLists(lists):
    h = []
    for i, lst in enumerate(lists):
        if lst:
            heapq.heappush(h, (lst[0], i, 0))
    res = []
    while h:
        val, i, j = heapq.heappop(h)
        res.append(val)
        if j + 1 < len(lists[i]):
            heapq.heappush(h, (lists[i][j + 1], i, j + 1))
    return res
