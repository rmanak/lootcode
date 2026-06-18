def minimumOneBitOperations(n):
    res = 0
    while n:
        res ^= n
        n >>= 1
    return res
