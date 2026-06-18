def longestHappyStringLength(a, b, c):
    import heapq
    heap = []
    if a:
        heapq.heappush(heap, (-a, 'a'))
    if b:
        heapq.heappush(heap, (-b, 'b'))
    if c:
        heapq.heappush(heap, (-c, 'c'))
    res = []
    while heap:
        cnt, ch = heapq.heappop(heap)
        cnt = -cnt
        if len(res) >= 2 and res[-1] == ch and res[-2] == ch:
            if not heap:
                break
            cnt2, ch2 = heapq.heappop(heap)
            cnt2 = -cnt2
            res.append(ch2)
            cnt2 -= 1
            if cnt2:
                heapq.heappush(heap, (-cnt2, ch2))
            heapq.heappush(heap, (-cnt, ch))
        else:
            res.append(ch)
            cnt -= 1
            if cnt:
                heapq.heappush(heap, (-cnt, ch))
    return len(res)
