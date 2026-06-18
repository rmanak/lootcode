def deleteAndEarn(nums):
    from collections import Counter
    cnt = Counter(nums)
    hi = max(nums)
    earn = [0] * (hi + 1)
    for v, c in cnt.items():
        earn[v] = v * c
    prev2, prev1 = 0, 0
    for v in range(hi + 1):
        prev2, prev1 = prev1, max(prev1, prev2 + earn[v])
    return prev1
