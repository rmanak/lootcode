def simplifiedFractions(n):
    from math import gcd
    res = []
    for d in range(2, n + 1):
        for num in range(1, d):
            if gcd(num, d) == 1:
                res.append(f"{num}/{d}")
    return res
