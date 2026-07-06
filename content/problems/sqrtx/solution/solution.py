def mySqrt(x):
    if x < 2:
        return x
    lo, hi = 1, x
    while lo <= hi:
        mid = (lo + hi) // 2
        if mid * mid <= x:
            lo = mid + 1
        else:
            hi = mid - 1
    return hi
