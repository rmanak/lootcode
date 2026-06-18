def minCost(n, cuts):
    from functools import lru_cache
    pts = sorted(set(cuts) | {0, n})
    m = len(pts)

    @lru_cache(None)
    def solve(i, j):
        if j - i <= 1:
            return 0
        return min(solve(i, t) + solve(t, j) + pts[j] - pts[i]
                   for t in range(i + 1, j))

    return solve(0, m - 1)
