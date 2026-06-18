def numSubarraysWithSum(A, S):
    from collections import defaultdict
    count = defaultdict(int)
    count[0] = 1
    cur = 0
    res = 0
    for x in A:
        cur += x
        res += count[cur - S]
        count[cur] += 1
    return res
