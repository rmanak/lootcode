def kConcatenationMaxSum(arr, k):
    MOD = 10 ** 9 + 7

    def kadane(a):
        best = cur = 0
        for x in a:
            cur = max(0, cur + x)
            best = max(best, cur)
        return best

    total = sum(arr)
    if k == 1:
        return kadane(arr) % MOD
    two = kadane(arr + arr)
    if total > 0:
        return (two + (k - 2) * total) % MOD
    return two % MOD
