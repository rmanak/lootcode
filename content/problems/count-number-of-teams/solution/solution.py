def numTeams(rating):
    n = len(rating)
    res = 0
    for j in range(n):
        less_left = sum(1 for i in range(j) if rating[i] < rating[j])
        great_left = j - less_left
        less_right = sum(1 for k in range(j + 1, n) if rating[k] < rating[j])
        great_right = (n - 1 - j) - less_right
        res += less_left * great_right + great_left * less_right
    return res
