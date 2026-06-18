def countDigitOne(n):
    if n < 0:
        return 0
    count = 0
    i = 1
    while i <= n:
        high = n // (i * 10)
        cur = (n // i) % 10
        low = n % i
        if cur == 0:
            count += high * i
        elif cur == 1:
            count += high * i + low + 1
        else:
            count += (high + 1) * i
        i *= 10
    return count
