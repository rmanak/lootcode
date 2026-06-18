def minCost(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    dirs = {1: (0, 1), 2: (0, -1), 3: (1, 0), 4: (-1, 0)}
    dist = [[float('inf')] * n for _ in range(m)]
    dist[0][0] = 0
    dq = deque([(0, 0)])
    while dq:
        i, j = dq.popleft()
        for d in range(1, 5):
            di, dj = dirs[d]
            ni, nj = i + di, j + dj
            cost = 0 if grid[i][j] == d else 1
            if 0 <= ni < m and 0 <= nj < n and dist[i][j] + cost < dist[ni][nj]:
                dist[ni][nj] = dist[i][j] + cost
                if cost == 0:
                    dq.appendleft((ni, nj))
                else:
                    dq.append((ni, nj))
    return dist[m - 1][n - 1]
