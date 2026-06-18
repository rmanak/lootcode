def maxCoins(piles):
    piles = sorted(piles)
    n = len(piles) // 3
    res = 0
    i = len(piles) - 2
    for _ in range(n):
        res += piles[i]
        i -= 2
    return res
