def minDeletionSize(strs):
    n = len(strs)
    m = len(strs[0])
    settled = [False] * (n - 1)
    res = 0
    for c in range(m):
        if any(not settled[i] and strs[i][c] > strs[i + 1][c]
               for i in range(n - 1)):
            res += 1
            continue
        for i in range(n - 1):
            if not settled[i] and strs[i][c] < strs[i + 1][c]:
                settled[i] = True
    return res
