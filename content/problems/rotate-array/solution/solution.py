def rotateArray(nums, k):
    n = len(nums)
    if n == 0:
        return list(nums)
    k %= n
    return list(nums[n - k:]) + list(nums[:n - k])
