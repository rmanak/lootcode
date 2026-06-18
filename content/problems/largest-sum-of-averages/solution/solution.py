def largestSumOfAverages(A, K):
    from functools import lru_cache
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]

    def avg(i, j):
        return (pre[j] - pre[i]) / (j - i)

    @lru_cache(None)
    def dp(i, k):
        if k == 1:
            return avg(i, n)
        best = 0.0
        for j in range(i + 1, n - k + 2):
            best = max(best, avg(i, j) + dp(j, k - 1))
        return best

    return round(dp(0, K), 5)
