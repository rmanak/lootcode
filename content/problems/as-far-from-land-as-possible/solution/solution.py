def maxDistance(grid):
    from collections import deque
    n = len(grid)
    m = len(grid[0])
    q = deque()
    seen = [[grid[i][j] == 1 for j in range(m)] for i in range(n)]
    for i in range(n):
        for j in range(m):
            if grid[i][j] == 1:
                q.append((i, j))
    if not q or len(q) == n * m:
        return -1
    dist = -1
    while q:
        dist += 1
        for _ in range(len(q)):
            i, j = q.popleft()
            for di, dj in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                ni, nj = i + di, j + dj
                if 0 <= ni < n and 0 <= nj < m and not seen[ni][nj]:
                    seen[ni][nj] = True
                    q.append((ni, nj))
    return dist
