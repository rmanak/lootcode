def findTargetSumWays(nums, S):
    from collections import defaultdict
    dp = defaultdict(int)
    dp[0] = 1
    for x in nums:
        ndp = defaultdict(int)
        for s, c in dp.items():
            ndp[s + x] += c
            ndp[s - x] += c
        dp = ndp
    return dp[S]
