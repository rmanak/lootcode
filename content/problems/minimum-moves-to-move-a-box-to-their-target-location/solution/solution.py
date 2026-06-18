def minPushBox(grid):
    import heapq
    m, n = len(grid), len(grid[0])
    box = player = target = None
    for i in range(m):
        for j in range(n):
            ch = grid[i][j]
            if ch == "B":
                box = (i, j)
            elif ch == "S":
                player = (i, j)
            elif ch == "T":
                target = (i, j)

    def ok(r, c):
        return 0 <= r < m and 0 <= c < n and grid[r][c] != "#"

    def reachable(start, end, blocked):
        if start == end:
            return True
        from collections import deque
        seen = {start, blocked}
        dq = deque([start])
        while dq:
            r, c = dq.popleft()
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if ok(nr, nc) and (nr, nc) not in seen:
                    if (nr, nc) == end:
                        return True
                    seen.add((nr, nc)); dq.append((nr, nc))
        return False

    dist = {(box, player): 0}
    pq = [(0, box, player)]
    while pq:
        d, b, p = heapq.heappop(pq)
        if b == target:
            return d
        if d > dist.get((b, p), 1 << 60):
            continue
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (b[0] + dr, b[1] + dc)
            pp = (b[0] - dr, b[1] - dc)
            if ok(*nb) and ok(*pp) and reachable(p, pp, b):
                ns = (nb, b)
                if d + 1 < dist.get(ns, 1 << 60):
                    dist[ns] = d + 1
                    heapq.heappush(pq, (d + 1, nb, b))
    return -1
