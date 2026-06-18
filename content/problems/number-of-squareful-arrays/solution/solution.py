def numSquarefulPerms(nums):
    from math import isqrt
    from collections import Counter

    def is_sq(x):
        r = isqrt(x)
        return r * r == x

    cnt = Counter(nums)
    total = [0]

    def dfs(prev, remaining):
        if remaining == 0:
            total[0] += 1
            return
        for x in list(cnt):
            if cnt[x] > 0 and (prev is None or is_sq(prev + x)):
                cnt[x] -= 1
                dfs(x, remaining - 1)
                cnt[x] += 1

    dfs(None, len(nums))
    return total[0]
