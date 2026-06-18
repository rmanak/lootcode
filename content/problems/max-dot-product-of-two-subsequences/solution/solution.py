def maxDotProduct(nums1, nums2):
    m, n = len(nums1), len(nums2)
    NEG = float('-inf')
    dp = [[NEG] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            prod = nums1[i - 1] * nums2[j - 1]
            dp[i][j] = max(prod, prod + max(dp[i - 1][j - 1], 0),
                           dp[i - 1][j], dp[i][j - 1])
    return dp[m][n]
