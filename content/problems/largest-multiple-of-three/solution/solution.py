def largestMultipleOfThree(digits):
    from collections import Counter
    total = sum(digits)
    r = total % 3
    m1 = sorted(d for d in digits if d % 3 == 1)
    m2 = sorted(d for d in digits if d % 3 == 2)
    remove = []
    if r == 1:
        if m1:
            remove = [m1[0]]
        elif len(m2) >= 2:
            remove = m2[:2]
        else:
            return ""
    elif r == 2:
        if m2:
            remove = [m2[0]]
        elif len(m1) >= 2:
            remove = m1[:2]
        else:
            return ""
    rc = Counter(remove)
    res = []
    for d in sorted(digits, reverse=True):
        if rc[d] > 0:
            rc[d] -= 1
        else:
            res.append(d)
    if not res:
        return ""
    if res[0] == 0:
        return "0"
    return "".join(map(str, res))
