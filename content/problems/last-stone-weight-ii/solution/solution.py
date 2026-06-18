def lastStoneWeightII(stones):
    total = sum(stones)
    half = total // 2
    dp = [False] * (half + 1)
    dp[0] = True
    for s in stones:
        for j in range(half, s - 1, -1):
            if dp[j - s]:
                dp[j] = True
    for j in range(half, -1, -1):
        if dp[j]:
            return total - 2 * j
