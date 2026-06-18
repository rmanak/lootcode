def numberOfArithmeticSlices(nums):
    n = len(nums)
    total = 0
    cur = 0
    for i in range(2, n):
        if nums[i] - nums[i - 1] == nums[i - 1] - nums[i - 2]:
            cur += 1
            total += cur
        else:
            cur = 0
    return total
