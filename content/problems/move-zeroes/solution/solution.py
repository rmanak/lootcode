def moveZeroes(nums):
    out = [x for x in nums if x != 0]
    out.extend(0 for x in nums if x == 0)
    return out
