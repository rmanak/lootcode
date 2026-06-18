def myPow(x, n):
    if n < 0:
        x = 1 / x
        n = -n
    result = 1.0
    base = x
    while n:
        if n & 1:
            result *= base
        base *= base
        n >>= 1
    return round(result, 6)
