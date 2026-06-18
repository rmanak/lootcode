def profitableSchemes(n, minProfit, group, profit):
    MOD = 10 ** 9 + 7
    dp = [[0] * (minProfit + 1) for _ in range(n + 1)]
    for g in range(n + 1):
        dp[g][0] = 1
    for k in range(len(group)):
        gk, pk = group[k], profit[k]
        for g in range(n, gk - 1, -1):
            for p in range(minProfit, -1, -1):
                np = min(minProfit, p + pk)
                dp[g][np] = (dp[g][np] + dp[g - gk][p]) % MOD
    return dp[n][minProfit] % MOD
