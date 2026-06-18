def findBestValue(arr, target):
    arr_sorted = sorted(arr)
    n = len(arr)
    pre = [0] * (n + 1)
    for i in range(n):
        pre[i + 1] = pre[i] + arr_sorted[i]
    import bisect

    def total(v):
        idx = bisect.bisect_right(arr_sorted, v)
        return pre[idx] + (n - idx) * v

    best, bd = 0, float('inf')
    for v in range(0, max(arr) + 1):
        d = abs(total(v) - target)
        if d < bd:
            bd, best = d, v
    return best
