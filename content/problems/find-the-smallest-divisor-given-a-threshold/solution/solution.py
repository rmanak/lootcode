def smallestDivisor(nums, threshold):
    lo, hi = 1, max(nums)
    while lo < hi:
        mid = (lo + hi) // 2
        s = sum((x + mid - 1) // mid for x in nums)
        if s <= threshold:
            hi = mid
        else:
            lo = mid + 1
    return lo
