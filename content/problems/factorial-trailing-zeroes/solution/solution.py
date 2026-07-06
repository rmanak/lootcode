def trailingZeroes(n):
    count = 0
    p = 5
    while p <= n:
        count += n // p
        p *= 5
    return count
