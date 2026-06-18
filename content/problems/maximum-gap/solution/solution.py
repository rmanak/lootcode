def maximumGap(nums):
    if len(nums) < 2:
        return 0
    lo, hi = min(nums), max(nums)
    if lo == hi:
        return 0
    n = len(nums)
    size = max(1, (hi - lo) // (n - 1))
    count = (hi - lo) // size + 1
    buckets = [[None, None] for _ in range(count)]
    for x in nums:
        b = (x - lo) // size
        bmin, bmax = buckets[b]
        buckets[b][0] = x if bmin is None else min(bmin, x)
        buckets[b][1] = x if bmax is None else max(bmax, x)
    best, prev_max = 0, lo
    for bmin, bmax in buckets:
        if bmin is None:
            continue
        best = max(best, bmin - prev_max)
        prev_max = bmax
    return best
