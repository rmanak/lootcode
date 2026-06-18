def containsCycle(grid):
    import sys
    sys.setrecursionlimit(10000)
    m = len(grid)
    n = len(grid[0])
    visited = [[False] * n for _ in range(m)]

    def dfs(r, c, pr, pc, val):
        visited[r][c] = True
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < m and 0 <= nc < n and grid[nr][nc] == val and not (nr == pr and nc == pc):
                if visited[nr][nc]:
                    return True
                if dfs(nr, nc, r, c, val):
                    return True
        return False

    for i in range(m):
        for j in range(n):
            if not visited[i][j] and dfs(i, j, -1, -1, grid[i][j]):
                return True
    return False
