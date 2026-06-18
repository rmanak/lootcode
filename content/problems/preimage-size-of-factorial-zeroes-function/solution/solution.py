def preimageSizeFZF(K):
    def f(x):
        c = 0
        while x > 0:
            x //= 5
            c += x
        return c

    lo, hi = 0, 5 * (K + 1)
    while lo < hi:
        mid = (lo + hi) // 2
        if f(mid) < K:
            lo = mid + 1
        else:
            hi = mid
    return 5 if f(lo) == K else 0
