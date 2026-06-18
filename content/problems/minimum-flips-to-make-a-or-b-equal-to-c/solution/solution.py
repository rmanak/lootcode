def minFlips(a, b, c):
    flips = 0
    while a or b or c:
        ai, bi, ci = a & 1, b & 1, c & 1
        if ci == 0:
            flips += ai + bi
        elif ai == 0 and bi == 0:
            flips += 1
        a >>= 1
        b >>= 1
        c >>= 1
    return flips
