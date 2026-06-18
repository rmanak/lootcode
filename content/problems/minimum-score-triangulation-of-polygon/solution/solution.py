def minScoreTriangulation(values):
    from functools import lru_cache
    n = len(values)

    @lru_cache(None)
    def dp(i, j):
        if j - i < 2:
            return 0
        best = float('inf')
        for k in range(i + 1, j):
            best = min(best, dp(i, k) + dp(k, j) + values[i] * values[k] * values[j])
        return best

    return dp(0, n - 1)
