def longestDupSubstring(s):
    n = len(s)
    lo, hi = 1, n - 1
    res = 0

    def has_dup(L):
        seen = set()
        for i in range(n - L + 1):
            sub = s[i:i + L]
            if sub in seen:
                return True
            seen.add(sub)
        return False

    while lo <= hi:
        mid = (lo + hi) // 2
        if has_dup(mid):
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res
