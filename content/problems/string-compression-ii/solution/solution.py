def getLengthOfOptimalCompression(s, k):
    from functools import lru_cache
    n = len(s)

    @lru_cache(None)
    def dp(i, prev, prev_cnt, k):
        if k < 0:
            return float('inf')
        if i == n:
            return 0
        res = dp(i + 1, prev, prev_cnt, k - 1)
        if s[i] == prev:
            incr = 1 if prev_cnt in (1, 9, 99) else 0
            res = min(res, incr + dp(i + 1, prev, prev_cnt + 1, k))
        else:
            res = min(res, 1 + dp(i + 1, s[i], 1, k))
        return res

    return dp(0, '', 0, k)
