def numOfMinutes(n, headID, manager, informTime):
    from collections import defaultdict, deque
    children = defaultdict(list)
    for i, m in enumerate(manager):
        if m != -1:
            children[m].append(i)
    best = 0
    q = deque([(headID, 0)])
    while q:
        node, t = q.popleft()
        best = max(best, t)
        for c in children[node]:
            q.append((c, t + informTime[node]))
    return best
