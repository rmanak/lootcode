def numOfSubarrays(arr):
    MOD = 10 ** 9 + 7
    odd = 0
    even = 1
    cur = 0
    res = 0
    for x in arr:
        cur += x
        if cur % 2 == 0:
            res = (res + odd) % MOD
            even += 1
        else:
            res = (res + even) % MOD
            odd += 1
    return res % MOD
