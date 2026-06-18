def numFactoredBinaryTrees(arr):
    MOD = 10 ** 9 + 7
    arr.sort()
    dp = {}
    for i, x in enumerate(arr):
        dp[x] = 1
        for j in range(i):
            y = arr[j]
            if x % y == 0 and x // y in dp:
                dp[x] = (dp[x] + dp[y] * dp[x // y]) % MOD
    return sum(dp.values()) % MOD
