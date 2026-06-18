def constrainedSubsetSum(nums, k):
    from collections import deque
    n = len(nums)
    dp = [0] * n
    dq = deque()
    res = float('-inf')
    for i in range(n):
        while dq and dq[0] < i - k:
            dq.popleft()
        best_prev = dp[dq[0]] if dq else 0
        dp[i] = nums[i] + max(best_prev, 0)
        res = max(res, dp[i])
        while dq and dp[dq[-1]] <= dp[i]:
            dq.pop()
        dq.append(i)
    return res
