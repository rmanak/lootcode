def minSteps(n):
    res = 0
    d = 2
    while n > 1:
        while n % d == 0:
            res += d
            n //= d
        d += 1
    return res
