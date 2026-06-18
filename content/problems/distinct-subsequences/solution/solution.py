def numDistinct(s, t):
    m = len(t)
    dp = [1] + [0] * m
    for ch in s:
        for j in range(m, 0, -1):
            if ch == t[j - 1]:
                dp[j] += dp[j - 1]
    return dp[m]
