def numDupDigitsAtMostN(n):
    digits = list(map(int, str(n)))
    L = len(digits)

    def perm(m, k):
        r = 1
        for i in range(k):
            r *= (m - i)
        return r

    res = 0
    for i in range(1, L):
        res += 9 * perm(9, i - 1)
    seen = set()
    for i, d in enumerate(digits):
        start = 1 if i == 0 else 0
        for x in range(start, d):
            if x not in seen:
                res += perm(9 - i, L - i - 1)
        if d in seen:
            break
        seen.add(d)
    else:
        res += 1
    return n - res
