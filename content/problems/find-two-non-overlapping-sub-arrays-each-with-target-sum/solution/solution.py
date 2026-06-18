def minSumOfLengths(arr, target):
    n = len(arr)
    INF = float('inf')
    pre = [INF] * n
    res = INF
    l = 0
    cur = 0
    best = INF
    for r in range(n):
        cur += arr[r]
        while cur > target:
            cur -= arr[l]
            l += 1
        if cur == target:
            length = r - l + 1
            if l > 0 and pre[l - 1] != INF:
                res = min(res, length + pre[l - 1])
            best = min(best, length)
        pre[r] = best
    return res if res != INF else -1
