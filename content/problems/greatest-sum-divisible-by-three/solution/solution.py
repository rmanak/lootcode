def maxSumDivThree(nums):
    NEG = float('-inf')
    dp = [0, NEG, NEG]
    for x in nums:
        ndp = dp[:]
        for r in range(3):
            if dp[r] > NEG:
                nr = (r + x) % 3
                ndp[nr] = max(ndp[nr], dp[r] + x)
        dp = ndp
    return dp[0]
