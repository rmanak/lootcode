def minDifficulty(jobDifficulty, d):
    n = len(jobDifficulty)
    if n < d:
        return -1
    from functools import lru_cache
    INF = float('inf')

    @lru_cache(None)
    def dp(i, days):
        if days == 1:
            return max(jobDifficulty[i:])
        best, mx = INF, 0
        for j in range(i, n - days + 1):
            mx = max(mx, jobDifficulty[j])
            best = min(best, mx + dp(j + 1, days - 1))
        return best

    return dp(0, d)
