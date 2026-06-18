def minOperations(nums, x):
    target = sum(nums) - x
    if target < 0:
        return -1
    if target == 0:
        return len(nums)
    best = -1
    left = s = 0
    for right, v in enumerate(nums):
        s += v
        while s > target and left <= right:
            s -= nums[left]
            left += 1
        if s == target:
            best = max(best, right - left + 1)
    return -1 if best < 0 else len(nums) - best
