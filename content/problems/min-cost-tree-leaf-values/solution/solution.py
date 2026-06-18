def mctFromLeafValues(arr):
    n = len(arr)
    maxv = [[0] * n for _ in range(n)]
    for i in range(n):
        m = arr[i]
        for j in range(i, n):
            m = max(m, arr[j])
            maxv[i][j] = m
    dp = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            dp[i][j] = min(dp[i][k] + dp[k + 1][j] + maxv[i][k] * maxv[k + 1][j]
                           for k in range(i, j))
    return dp[0][n - 1]
