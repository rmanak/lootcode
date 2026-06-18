def superPow(a, b):
    MOD = 1337
    res = 1
    a %= MOD
    for d in b:
        res = pow(res, 10, MOD) * pow(a, d, MOD) % MOD
    return res
