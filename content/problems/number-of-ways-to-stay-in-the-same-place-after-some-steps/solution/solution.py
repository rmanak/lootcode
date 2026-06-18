def numWays(steps, arrLen):
    MOD = 10 ** 9 + 7
    maxpos = min(steps // 2 + 1, arrLen)
    dp = [0] * maxpos
    dp[0] = 1
    for _ in range(steps):
        ndp = [0] * maxpos
        for i in range(maxpos):
            v = dp[i]
            if v:
                ndp[i] = (ndp[i] + v) % MOD
                if i > 0:
                    ndp[i - 1] = (ndp[i - 1] + v) % MOD
                if i + 1 < maxpos:
                    ndp[i + 1] = (ndp[i + 1] + v) % MOD
        dp = ndp
    return dp[0] % MOD
