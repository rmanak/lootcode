def countRangeSum(nums, lower, upper):
    prefix = [0]
    for x in nums:
        prefix.append(prefix[-1] + x)

    def msort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = msort(lo, mid) + msort(mid, hi)
        j = k = mid
        for i in range(lo, mid):
            while j < hi and prefix[j] - prefix[i] < lower:
                j += 1
            while k < hi and prefix[k] - prefix[i] <= upper:
                k += 1
            cnt += k - j
        prefix[lo:hi] = sorted(prefix[lo:hi])
        return cnt

    return msort(0, len(prefix))
