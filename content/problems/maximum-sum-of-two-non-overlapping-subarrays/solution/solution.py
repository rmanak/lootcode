def maxSumTwoNoOverlap(A, L, M):
    n = len(A)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + A[i]

    def helper(Lx, Mx):
        res = 0
        max_l = 0
        for j in range(Lx + Mx, n + 1):
            max_l = max(max_l, pre[j - Mx] - pre[j - Mx - Lx])
            res = max(res, max_l + pre[j] - pre[j - Mx])
        return res

    return max(helper(L, M), helper(M, L))
