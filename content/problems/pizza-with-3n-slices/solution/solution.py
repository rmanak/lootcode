def maxSizeSlices(slices):
    n = len(slices)
    k = n // 3
    NEG = float('-inf')

    def solve(arr):
        m = len(arr)
        dp = [[NEG] * (k + 1) for _ in range(m + 1)]
        for i in range(m + 1):
            dp[i][0] = 0
        for i in range(1, m + 1):
            for j in range(1, k + 1):
                take = arr[i - 1] + (dp[i - 2][j - 1] if i >= 2 else (0 if j == 1 else NEG))
                dp[i][j] = max(dp[i - 1][j], take)
        return dp[m][k]

    return max(solve(slices[1:]), solve(slices[:-1]))
