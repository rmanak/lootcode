def minOperations(n):
    res = 0
    for i in range(n // 2):
        res += n - (2 * i + 1)
    return res
