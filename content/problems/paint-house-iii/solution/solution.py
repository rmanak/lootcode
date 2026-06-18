def minCost(houses, cost, m, n, target):
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, prev, groups):
        if groups > target:
            return INF
        if i == m:
            return 0 if groups == target else INF
        if houses[i] != 0:
            c = houses[i]
            return dp(i + 1, c, groups + (1 if c != prev else 0))
        best = INF
        for c in range(1, n + 1):
            best = min(best, cost[i][c - 1] +
                       dp(i + 1, c, groups + (1 if c != prev else 0)))
        return best

    res = dp(0, 0, 0)
    return res if res != INF else -1
