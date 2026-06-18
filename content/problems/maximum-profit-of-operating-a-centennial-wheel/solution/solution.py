def minOperationsMaxProfit(customers, boardingCost, runningCost):
    waiting = 0
    profit = 0
    best_profit = 0
    best_rot = -1
    rot = 0
    i = 0
    n = len(customers)
    while i < n or waiting > 0:
        if i < n:
            waiting += customers[i]
            i += 1
        board = min(4, waiting)
        waiting -= board
        rot += 1
        profit += board * boardingCost - runningCost
        if profit > best_profit:
            best_profit = profit
            best_rot = rot
    return best_rot
