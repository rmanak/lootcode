def canSum(nums, target):
    if target < 0:
        return False
    bits = 1
    for x in nums:
        bits |= bits << x
    return bool((bits >> target) & 1)
