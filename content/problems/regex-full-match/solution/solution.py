def isMatch(s, p):
    from functools import lru_cache

    @lru_cache(None)
    def dp(i, j):
        if j == len(p):
            return i == len(s)
        first = i < len(s) and (p[j] == s[i] or p[j] == '.')
        if j + 1 < len(p) and p[j + 1] == '*':
            return dp(i, j + 2) or (first and dp(i + 1, j))
        return first and dp(i + 1, j + 1)

    return dp(0, 0)
