def subarraysDivByK(A, K):
    from collections import defaultdict
    cnt = defaultdict(int)
    cnt[0] = 1
    pre = 0
    res = 0
    for x in A:
        pre = (pre + x) % K
        res += cnt[pre]
        cnt[pre] += 1
    return res
