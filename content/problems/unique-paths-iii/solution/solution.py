def uniquePathsIII(grid):
    m, n = len(grid), len(grid[0])
    empty = 1
    sr = sc = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 0:
                empty += 1
            elif grid[i][j] == 1:
                sr, sc = i, j

    def dfs(i, j, remaining):
        if grid[i][j] == 2:
            return 1 if remaining == 0 else 0
        if grid[i][j] == -1:
            return 0
        save = grid[i][j]
        grid[i][j] = -1
        total = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            ni, nj = i + dr, j + dc
            if 0 <= ni < m and 0 <= nj < n:
                total += dfs(ni, nj, remaining - 1)
        grid[i][j] = save
        return total

    return dfs(sr, sc, empty)
