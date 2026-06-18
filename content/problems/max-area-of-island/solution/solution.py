def maxAreaOfIsland(grid):
    m, n = len(grid), len(grid[0])
    seen = [[False] * n for _ in range(m)]
    best = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and not seen[i][j]:
                area = 0
                stack = [(i, j)]
                seen[i][j] = True
                while stack:
                    x, y = stack.pop()
                    area += 1
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < m and 0 <= ny < n and grid[nx][ny] == 1                                 and not seen[nx][ny]:
                            seen[nx][ny] = True
                            stack.append((nx, ny))
                best = max(best, area)
    return best
