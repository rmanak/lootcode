def maxScore(cardPoints, k):
    n = len(cardPoints)
    w = n - k
    if w == 0:
        return sum(cardPoints)
    cur = sum(cardPoints[:w])
    min_win = cur
    for i in range(w, n):
        cur += cardPoints[i] - cardPoints[i - w]
        min_win = min(min_win, cur)
    return sum(cardPoints) - min_win
