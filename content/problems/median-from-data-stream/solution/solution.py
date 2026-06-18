def medianStream(operations):
    import heapq
    small, large, out = [], [], []
    for op in operations:
        if op[0] == "addNum":
            heapq.heappush(small, -op[1])
            heapq.heappush(large, -heapq.heappop(small))
            if len(large) > len(small):
                heapq.heappush(small, -heapq.heappop(large))
            out.append(None)
        else:
            if len(small) > len(large):
                out.append(float(-small[0]))
            else:
                out.append((-small[0] + large[0]) / 2)
    return out
