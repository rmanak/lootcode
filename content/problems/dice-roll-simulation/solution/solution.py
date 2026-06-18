def dieSimulator(n, rollMax):
    MOD = 10 ** 9 + 7
    dp = [[0] * (rollMax[j] + 1) for j in range(6)]
    for j in range(6):
        dp[j][1] = 1
    for _ in range(n - 1):
        ndp = [[0] * (rollMax[j] + 1) for j in range(6)]
        for j in range(6):
            total_j = sum(dp[j]) % MOD
            for k in range(1, rollMax[j]):
                ndp[j][k + 1] = (ndp[j][k + 1] + dp[j][k]) % MOD
            for x in range(6):
                if x != j:
                    ndp[x][1] = (ndp[x][1] + total_j) % MOD
        dp = ndp
    return sum(sum(row) for row in dp) % MOD
