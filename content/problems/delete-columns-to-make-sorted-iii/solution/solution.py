def minDeletionSize(A):
    n = len(A[0])
    dp = [1] * n
    for j in range(n):
        for i in range(j):
            if all(row[i] <= row[j] for row in A):
                dp[j] = max(dp[j], dp[i] + 1)
    return n - max(dp)
