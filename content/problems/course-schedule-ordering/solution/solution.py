def findOrder(numCourses, prerequisites):
    import heapq
    from collections import defaultdict
    adj = defaultdict(list)
    indeg = [0] * numCourses
    for a, b in prerequisites:
        adj[b].append(a)
        indeg[a] += 1
    heap = [i for i in range(numCourses) if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        u = heapq.heappop(heap)
        order.append(u)
        for v in adj[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, v)
    return order if len(order) == numCourses else []
