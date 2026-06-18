def combinationSum4(nums, target):
    dp = [0] * (target + 1)
    dp[0] = 1
    for t in range(1, target + 1):
        for x in nums:
            if x <= t:
                dp[t] += dp[t - x]
    return dp[target]
