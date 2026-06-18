def nthUglyNumber(n):
    ugly = [1] * n
    i2 = i3 = i5 = 0
    for i in range(1, n):
        nxt = min(ugly[i2] * 2, ugly[i3] * 3, ugly[i5] * 5)
        ugly[i] = nxt
        if nxt == ugly[i2] * 2:
            i2 += 1
        if nxt == ugly[i3] * 3:
            i3 += 1
        if nxt == ugly[i5] * 5:
            i5 += 1
    return ugly[-1]
