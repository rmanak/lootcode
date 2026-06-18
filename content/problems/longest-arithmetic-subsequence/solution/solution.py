def longestArithSeqLength(nums):
    n = len(nums)
    if n <= 1:
        return n
    dp = [{} for _ in range(n)]
    best = 1
    for i in range(n):
        for j in range(i):
            d = nums[i] - nums[j]
            dp[i][d] = dp[j].get(d, 1) + 1
            best = max(best, dp[i][d])
    return best
