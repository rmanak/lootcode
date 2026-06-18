def kClosest(points, k):
    import heapq
    return heapq.nsmallest(k, points, key=lambda p: p[0] * p[0] + p[1] * p[1])
