def smallestDistancePair(nums, k):
    nums = sorted(nums)
    n = len(nums)

    def count(d):
        cnt = 0
        j = 0
        for i in range(n):
            while nums[i] - nums[j] > d:
                j += 1
            cnt += i - j
        return cnt

    lo, hi = 0, nums[-1] - nums[0]
    while lo < hi:
        mid = (lo + hi) // 2
        if count(mid) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo
