def splitArray(nums, m):
    lo, hi = max(nums), sum(nums)

    def need(cap):
        cnt, cur = 1, 0
        for x in nums:
            if cur + x > cap:
                cnt += 1
                cur = x
            else:
                cur += x
        return cnt

    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= m:
            hi = mid
        else:
            lo = mid + 1
    return lo
