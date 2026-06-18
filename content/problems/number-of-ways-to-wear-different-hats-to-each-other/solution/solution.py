def numberWays(hats):
    MOD = 10 ** 9 + 7
    n = len(hats)
    hat_people = [[] for _ in range(41)]
    for i, hs in enumerate(hats):
        for h in hs:
            hat_people[h].append(i)
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[0] = 1
    for hat in range(1, 41):
        ndp = dp[:]
        for mask in range(1 << n):
            if dp[mask] == 0:
                continue
            for p in hat_people[hat]:
                if not (mask >> p) & 1:
                    nm = mask | (1 << p)
                    ndp[nm] = (ndp[nm] + dp[mask]) % MOD
        dp = ndp
    return dp[full] % MOD
