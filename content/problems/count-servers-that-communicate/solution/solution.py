def countServers(grid):
    m, n = len(grid), len(grid[0])
    row_count = [sum(r) for r in grid]
    col_count = [sum(grid[i][j] for i in range(m)) for j in range(n)]
    res = 0
    for i in range(m):
        for j in range(n):
            if grid[i][j] == 1 and (row_count[i] > 1 or col_count[j] > 1):
                res += 1
    return res
