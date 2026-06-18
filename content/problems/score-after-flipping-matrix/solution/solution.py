def matrixScore(grid):
    m, n = len(grid), len(grid[0])
    g = [row[:] for row in grid]
    for i in range(m):
        if g[i][0] == 0:
            g[i] = [1 - x for x in g[i]]
    total = 0
    for j in range(n):
        ones = sum(g[i][j] for i in range(m))
        ones = max(ones, m - ones)
        total += ones * (1 << (n - 1 - j))
    return total
