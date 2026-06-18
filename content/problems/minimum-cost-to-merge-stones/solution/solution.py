def mergeStones(stones, K):
    n = len(stones)
    if (n - 1) % (K - 1) != 0:
        return -1
    prefix = [0] * (n + 1)
    for i in range(n):
        prefix[i + 1] = prefix[i] + stones[i]
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, j):
        if i == j:
            return 0
        res = INF
        for m in range(i, j, K - 1):
            res = min(res, dp(i, m) + dp(m + 1, j))
        if (j - i) % (K - 1) == 0:
            res += prefix[j + 1] - prefix[i]
        return res

    return dp(0, n - 1)
