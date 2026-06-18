def maxProfit(prices):
    if not prices:
        return 0
    hold = -prices[0]
    sold = 0
    rest = 0
    for p in prices[1:]:
        prev_sold = sold
        sold = hold + p
        hold = max(hold, rest - p)
        rest = max(rest, prev_sold)
    return max(sold, rest)
