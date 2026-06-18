def new21Game(N, K, W):
    if K == 0 or N >= K - 1 + W:
        return 1.0
    dp = [0.0] * (N + 1)
    dp[0] = 1.0
    Wsum = 1.0
    res = 0.0
    for i in range(1, N + 1):
        dp[i] = Wsum / W
        if i < K:
            Wsum += dp[i]
        else:
            res += dp[i]
        if 0 <= i - W < K:
            Wsum -= dp[i - W]
    return round(res, 5)
