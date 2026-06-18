def longestSubsequence(arr, difference):
    dp = {}
    best = 0
    for x in arr:
        dp[x] = dp.get(x - difference, 0) + 1
        best = max(best, dp[x])
    return best
