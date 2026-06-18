def isGoodArray(nums):
    from math import gcd
    from functools import reduce
    return reduce(gcd, nums) == 1
