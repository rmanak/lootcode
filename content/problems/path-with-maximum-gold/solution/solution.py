def getMaximumGold(grid):
    grid = [row[:] for row in grid]
    m, n = len(grid), len(grid[0])
    best = [0]

    def dfs(i, j, cur):
        cur += grid[i][j]
        best[0] = max(best[0], cur)
        keep = grid[i][j]
        grid[i][j] = 0
        for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + di, j + dj
            if 0 <= ni < m and 0 <= nj < n and grid[ni][nj] != 0:
                dfs(ni, nj, cur)
        grid[i][j] = keep

    for i in range(m):
        for j in range(n):
            if grid[i][j] != 0:
                dfs(i, j, 0)
    return best[0]
