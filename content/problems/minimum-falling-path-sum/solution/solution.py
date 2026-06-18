def minFallingPathSum(matrix):
    rows, cols = len(matrix), len(matrix[0])
    dp = list(matrix[0])
    for r in range(1, rows):
        ndp = [0] * cols
        for c in range(cols):
            best = dp[c]
            if c > 0:
                best = min(best, dp[c - 1])
            if c < cols - 1:
                best = min(best, dp[c + 1])
            ndp[c] = matrix[r][c] + best
        dp = ndp
    return min(dp)
