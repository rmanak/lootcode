def nthUglyNumber(n, a, b, c):
    from math import gcd

    def lcm(x, y):
        return x * y // gcd(x, y)

    ab, ac, bc = lcm(a, b), lcm(a, c), lcm(b, c)
    abc = lcm(ab, c)

    def count(x):
        return x // a + x // b + x // c - x // ab - x // ac - x // bc + x // abc

    lo, hi = 1, 2 * 10 ** 9
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= n:
            hi = mid
        else:
            lo = mid + 1
    return lo
