def distinctSubseqII(S):
    MOD = 10 ** 9 + 7
    end = {}
    for c in S:
        end[c] = (sum(end.values()) + 1) % MOD
    return sum(end.values()) % MOD
