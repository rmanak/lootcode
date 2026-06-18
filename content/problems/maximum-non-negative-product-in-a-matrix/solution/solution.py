def maxProductPath(grid):
    MOD = 10 ** 9 + 7
    m, n = len(grid), len(grid[0])
    mx = [[0] * n for _ in range(m)]
    mn = [[0] * n for _ in range(m)]
    mx[0][0] = mn[0][0] = grid[0][0]
    for i in range(m):
        for j in range(n):
            if i == 0 and j == 0:
                continue
            g = grid[i][j]
            cand = []
            if i > 0:
                cand += [mx[i - 1][j] * g, mn[i - 1][j] * g]
            if j > 0:
                cand += [mx[i][j - 1] * g, mn[i][j - 1] * g]
            mx[i][j] = max(cand)
            mn[i][j] = min(cand)
    res = mx[m - 1][n - 1]
    return res % MOD if res >= 0 else -1
