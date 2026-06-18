def maximumScore(nums, multipliers):
    n, m = len(nums), len(multipliers)
    dp = [0] * (m + 1)
    for i in range(m - 1, -1, -1):
        ndp = [0] * (m + 1)
        for left in range(i, -1, -1):
            right = n - 1 - (i - left)
            ndp[left] = max(multipliers[i] * nums[left] + dp[left + 1],
                            multipliers[i] * nums[right] + dp[left])
        dp = ndp
    return dp[0]
