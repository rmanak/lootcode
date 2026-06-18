def threeSumClosest(nums, target):
    nums = sorted(nums)
    n = len(nums)
    best = nums[0] + nums[1] + nums[2]
    for i in range(n - 2):
        lo, hi = i + 1, n - 1
        while lo < hi:
            s = nums[i] + nums[lo] + nums[hi]
            if abs(s - target) < abs(best - target) or                     (abs(s - target) == abs(best - target) and s < best):
                best = s
            if s == target:
                return s
            if s < target:
                lo += 1
            else:
                hi -= 1
    return best
