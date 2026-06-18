def numSubarrayProductLessThanK(nums, k):
    if k <= 1:
        return 0
    prod = 1
    left = cnt = 0
    for right, v in enumerate(nums):
        prod *= v
        while prod >= k:
            prod //= nums[left]
            left += 1
        cnt += right - left + 1
    return cnt
