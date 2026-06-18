def minDays(bloomDay, m, k):
    n = len(bloomDay)
    if m * k > n:
        return -1

    def can(day):
        bouquets = flowers = 0
        for b in bloomDay:
            if b <= day:
                flowers += 1
                if flowers == k:
                    bouquets += 1
                    flowers = 0
            else:
                flowers = 0
        return bouquets >= m

    lo, hi = min(bloomDay), max(bloomDay)
    while lo < hi:
        mid = (lo + hi) // 2
        if can(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo
