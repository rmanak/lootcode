def shipWithinDays(weights, days):
    lo, hi = max(weights), sum(weights)

    def need(cap):
        d, cur = 1, 0
        for w in weights:
            if cur + w > cap:
                d += 1
                cur = w
            else:
                cur += w
        return d

    while lo < hi:
        mid = (lo + hi) // 2
        if need(mid) <= days:
            hi = mid
        else:
            lo = mid + 1
    return lo
