def knapsack(values, weights, capacity):
    dp = [0] * (capacity + 1)
    for v, w in zip(values, weights):
        for c in range(capacity, w - 1, -1):
            dp[c] = max(dp[c], dp[c - w] + v)
    return dp[capacity]
