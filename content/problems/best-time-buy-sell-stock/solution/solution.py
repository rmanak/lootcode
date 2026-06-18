def maxProfit(prices):
    best = 0
    lo = float('inf')
    for p in prices:
        lo = min(lo, p)
        best = max(best, p - lo)
    return best
