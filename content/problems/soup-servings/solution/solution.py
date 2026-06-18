def soupServings(n):
    if n >= 4800:
        return 1.0
    from functools import lru_cache
    m = (n + 24) // 25

    @lru_cache(None)
    def dp(a, b):
        if a <= 0 and b <= 0:
            return 0.5
        if a <= 0:
            return 1.0
        if b <= 0:
            return 0.0
        return 0.25 * (dp(a - 4, b) + dp(a - 3, b - 1) +
                       dp(a - 2, b - 2) + dp(a - 1, b - 3))

    return round(dp(m, m), 5)
