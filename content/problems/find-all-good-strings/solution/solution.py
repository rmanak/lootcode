def findGoodStrings(n, s1, s2, evil):
    MOD = 10 ** 9 + 7
    m = len(evil)
    fail = [0] * m
    k = 0
    for i in range(1, m):
        while k > 0 and evil[i] != evil[k]:
            k = fail[k - 1]
        if evil[i] == evil[k]:
            k += 1
        fail[i] = k

    def trans(j, c):
        while j > 0 and c != evil[j]:
            j = fail[j - 1]
        if c == evil[j]:
            j += 1
        return j

    from functools import lru_cache

    @lru_cache(None)
    def dp(pos, matched, lowtight, hightight):
        if matched == m:
            return 0
        if pos == n:
            return 1
        lo = ord(s1[pos]) - 97 if lowtight else 0
        hi = ord(s2[pos]) - 97 if hightight else 25
        total = 0
        for c in range(lo, hi + 1):
            total += dp(pos + 1, trans(matched, chr(c + 97)),
                        lowtight and c == lo, hightight and c == hi)
        return total % MOD

    return dp(0, 0, True, True) % MOD
