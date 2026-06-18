def largestNumber(cost, target):
    dp = [0] + [-1] * target
    for t in range(1, target + 1):
        for c in cost:
            if t - c >= 0 and dp[t - c] != -1:
                dp[t] = max(dp[t], dp[t - c] + 1)
    if dp[target] == -1:
        return "0"
    res = []
    t = target
    for d in range(9, 0, -1):
        c = cost[d - 1]
        while t - c >= 0 and dp[t - c] == dp[t] - 1:
            res.append(str(d))
            t -= c
    return "".join(res)
