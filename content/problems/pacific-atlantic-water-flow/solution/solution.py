def pacificAtlantic(heights):
    if not heights or not heights[0]:
        return []
    m, n = len(heights), len(heights[0])
    pac = [[False] * n for _ in range(m)]
    atl = [[False] * n for _ in range(m)]
    def dfs(r, c, vis, prev):
        if r < 0 or c < 0 or r >= m or c >= n or vis[r][c] or heights[r][c] < prev:
            return
        vis[r][c] = True
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            dfs(r + dr, c + dc, vis, heights[r][c])
    for i in range(m):
        dfs(i, 0, pac, heights[i][0])
        dfs(i, n - 1, atl, heights[i][n - 1])
    for j in range(n):
        dfs(0, j, pac, heights[0][j])
        dfs(m - 1, j, atl, heights[m - 1][j])
    res = [[i, j] for i in range(m) for j in range(n) if pac[i][j] and atl[i][j]]
    res.sort()
    return res
