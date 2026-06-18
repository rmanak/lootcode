def leastOpsExpressTarget(x, target):
    from functools import lru_cache

    @lru_cache(None)
    def dp(t):
        if t == 0:
            return 0
        if t < x:
            return min(2 * t - 1, 2 * (x - t))
        k = 0
        p = 1
        while p * x <= t:
            p *= x
            k += 1
        rem = t - p
        cost_under = (k - 1) + (0 if rem == 0 else 1 + dp(rem))
        rem2 = p * x - t
        if rem2 < t:
            return min(cost_under, k + 1 + dp(rem2))
        return cost_under

    return dp(target)
