def minDifference(nums):
    n = len(nums)
    if n <= 4:
        return 0
    nums.sort()
    return min(nums[n - 4 + i] - nums[i] for i in range(4))
