def maxScoreSightseeing(values):
    best = values[0]
    ans = float('-inf')
    for j in range(1, len(values)):
        ans = max(ans, best + values[j] - j)
        best = max(best, values[j] + j)
    return ans
