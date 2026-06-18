def countSquares(matrix):
    m, n = len(matrix), len(matrix[0])
    dp = [[0] * n for _ in range(m)]
    total = 0
    for r in range(m):
        for c in range(n):
            if matrix[r][c] == 1:
                if r == 0 or c == 0:
                    dp[r][c] = 1
                else:
                    dp[r][c] = 1 + min(dp[r - 1][c], dp[r][c - 1], dp[r - 1][c - 1])
                total += dp[r][c]
    return total
