def nthMagicalNumber(n, a, b):
    from math import gcd
    MOD = 10 ** 9 + 7
    l = a * b // gcd(a, b)
    lo, hi = 1, n * min(a, b)
    while lo < hi:
        mid = (lo + hi) // 2
        if mid // a + mid // b - mid // l >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo % MOD
