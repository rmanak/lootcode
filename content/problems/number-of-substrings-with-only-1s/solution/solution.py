def numSub(s):
    MOD = 10 ** 9 + 7
    res = 0
    run = 0
    for c in s:
        if c == '1':
            run += 1
            res = (res + run) % MOD
        else:
            run = 0
    return res % MOD
