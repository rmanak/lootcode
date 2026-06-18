def isScramble(s1, s2):
    from functools import lru_cache

    @lru_cache(None)
    def helper(a, b):
        if a == b:
            return True
        if sorted(a) != sorted(b):
            return False
        n = len(a)
        for i in range(1, n):
            if helper(a[:i], b[:i]) and helper(a[i:], b[i:]):
                return True
            if helper(a[:i], b[n - i:]) and helper(a[i:], b[:n - i]):
                return True
        return False

    return helper(s1, s2)
