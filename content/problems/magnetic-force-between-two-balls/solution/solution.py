def maxDistance(position, m):
    position = sorted(position)

    def feasible(d):
        count = 1
        last = position[0]
        for p in position[1:]:
            if p - last >= d:
                count += 1
                last = p
        return count >= m

    lo, hi = 1, position[-1] - position[0]
    res = 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            res = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return res
