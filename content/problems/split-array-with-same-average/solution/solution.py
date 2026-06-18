def splitArraySameAverage(nums):
    n = len(nums)
    total = sum(nums)
    dp = [set() for _ in range(n // 2 + 1)]
    dp[0].add(0)
    for x in nums:
        for k in range(len(dp) - 1, 0, -1):
            for s in dp[k - 1]:
                dp[k].add(s + x)
    for k in range(1, n // 2 + 1):
        if total * k % n == 0 and (total * k // n) in dp[k]:
            return True
    return False
