def maximumUniqueSubarray(nums):
    seen = set()
    left = s = best = 0
    for v in nums:
        while v in seen:
            seen.remove(nums[left])
            s -= nums[left]
            left += 1
        seen.add(v)
        s += v
        best = max(best, s)
    return best
