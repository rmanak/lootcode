def countOrders(n):
    MOD = 10 ** 9 + 7
    res = 1
    for i in range(1, n + 1):
        res = res * i * (2 * i - 1) % MOD
    return res
