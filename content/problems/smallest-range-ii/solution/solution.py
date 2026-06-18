def smallestRangeII(A, K):
    A = sorted(A)
    n = len(A)
    res = A[-1] - A[0]
    for i in range(n - 1):
        hi = max(A[-1] - K, A[i] + K)
        lo = min(A[0] + K, A[i + 1] - K)
        res = min(res, hi - lo)
    return res
