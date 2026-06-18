def findItinerary(tickets):
    from collections import defaultdict
    import heapq
    graph = defaultdict(list)
    for a, b in tickets:
        heapq.heappush(graph[a], b)
    route, stack = [], ["JFK"]
    while stack:
        while graph[stack[-1]]:
            stack.append(heapq.heappop(graph[stack[-1]]))
        route.append(stack.pop())
    return route[::-1]
