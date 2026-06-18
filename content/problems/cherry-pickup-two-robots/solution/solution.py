def cherryPickup(grid):
    rows, cols = len(grid), len(grid[0])
    neg = float('-inf')
    dp = [[grid[rows - 1][c1] + (grid[rows - 1][c2] if c1 != c2 else 0)
           for c2 in range(cols)] for c1 in range(cols)]
    for r in range(rows - 2, -1, -1):
        ndp = [[neg] * cols for _ in range(cols)]
        for c1 in range(cols):
            for c2 in range(cols):
                base = grid[r][c1] + (grid[r][c2] if c1 != c2 else 0)
                best = neg
                for nc1 in (c1 - 1, c1, c1 + 1):
                    for nc2 in (c2 - 1, c2, c2 + 1):
                        if 0 <= nc1 < cols and 0 <= nc2 < cols:
                            best = max(best, dp[nc1][nc2])
                ndp[c1][c2] = base + best
        dp = ndp
    return dp[0][cols - 1]
