def knightDialer(n):
    MOD = 10 ** 9 + 7
    moves = {0: [4, 6], 1: [6, 8], 2: [7, 9], 3: [4, 8], 4: [0, 3, 9],
             5: [], 6: [0, 1, 7], 7: [2, 6], 8: [1, 3], 9: [2, 4]}
    dp = [1] * 10
    for _ in range(n - 1):
        ndp = [0] * 10
        for d in range(10):
            for nx in moves[d]:
                ndp[nx] = (ndp[nx] + dp[d]) % MOD
        dp = ndp
    return sum(dp) % MOD
