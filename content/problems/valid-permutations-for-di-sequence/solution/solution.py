def numPermsDISequence(S):
    MOD = 10 ** 9 + 7
    n = len(S)
    dp = [1]
    for i in range(n):
        c = S[i]
        L = i + 1
        pre = [0] * (L + 1)
        for j in range(L):
            pre[j + 1] = (pre[j] + dp[j]) % MOD
        ndp = [0] * (L + 1)
        for j in range(L + 1):
            if c == 'I':
                ndp[j] = pre[j]
            else:
                ndp[j] = (pre[L] - pre[j]) % MOD
        dp = ndp
    return sum(dp) % MOD
