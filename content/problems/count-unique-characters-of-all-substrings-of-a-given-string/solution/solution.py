def uniqueLetterString(s):
    MOD = 10 ** 9 + 7
    from collections import defaultdict
    idx = defaultdict(lambda: [-1, -1])
    res = 0
    for i, c in enumerate(s):
        prev2, prev1 = idx[c]
        res += (prev1 - prev2) * (i - prev1)
        idx[c] = [prev1, i]
    n = len(s)
    for c in idx:
        prev2, prev1 = idx[c]
        res += (prev1 - prev2) * (n - prev1)
    return res % MOD
