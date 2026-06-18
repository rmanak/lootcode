def singleNumber(nums):
    r = 0
    for x in nums:
        r ^= x
    return r
