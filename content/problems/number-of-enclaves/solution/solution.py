def numEnclaves(grid):
    from collections import deque
    m, n = len(grid), len(grid[0])
    grid = [row[:] for row in grid]
    q = deque()
    for r in range(m):
        for c in range(n):
            if (r in (0, m - 1) or c in (0, n - 1)) and grid[r][c] == 1:
                grid[r][c] = 0
                q.append((r, c))
    while q:
        r, c = q.popleft()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == 1:
                grid[nr][nc] = 0
                q.append((nr, nc))
    return sum(sum(row) for row in grid)
