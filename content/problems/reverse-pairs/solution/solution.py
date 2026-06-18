def reversePairs(nums):
    def msort(lo, hi):
        if hi - lo <= 1:
            return 0
        mid = (lo + hi) // 2
        cnt = msort(lo, mid) + msort(mid, hi)
        j = mid
        for i in range(lo, mid):
            while j < hi and nums[i] > 2 * nums[j]:
                j += 1
            cnt += j - mid
        nums[lo:hi] = sorted(nums[lo:hi])
        return cnt

    return msort(0, len(nums))
