def minDays(n):
    from functools import lru_cache

    @lru_cache(None)
    def f(x):
        if x <= 1:
            return x
        return 1 + min(x % 2 + f(x // 2), x % 3 + f(x // 3))

    return f(n)
