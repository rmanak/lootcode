def maxProfit(prices, k):
    n = len(prices)
    if n == 0 or k == 0:
        return 0
    if k >= n // 2:
        return sum(max(0, prices[i + 1] - prices[i]) for i in range(n - 1))
    buy = [float('-inf')] * (k + 1)
    sell = [0] * (k + 1)
    for p in prices:
        for t in range(1, k + 1):
            buy[t] = max(buy[t], sell[t - 1] - p)
            sell[t] = max(sell[t], buy[t] + p)
    return sell[k]
