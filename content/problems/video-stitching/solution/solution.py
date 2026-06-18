def videoStitching(clips, T):
    INF = float("inf")
    dp = [0] + [INF] * T
    for i in range(1, T + 1):
        for s, e in clips:
            if s < i <= e and dp[s] + 1 < dp[i]:
                dp[i] = dp[s] + 1
    return -1 if dp[T] == INF else dp[T]
