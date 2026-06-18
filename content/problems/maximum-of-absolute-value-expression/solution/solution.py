def maxAbsValExpr(arr1, arr2):
    n = len(arr1)
    res = 0
    for s1 in (1, -1):
        for s2 in (1, -1):
            mx = float('-inf')
            mn = float('inf')
            for i in range(n):
                val = s1 * arr1[i] + s2 * arr2[i] + i
                mx = max(mx, val)
                mn = min(mn, val)
            res = max(res, mx - mn)
    return res
