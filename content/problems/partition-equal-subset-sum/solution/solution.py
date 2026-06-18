def canPartition(nums):
    total = sum(nums)
    if total % 2:
        return False
    target = total // 2
    bits = 1
    for x in nums:
        bits |= bits << x
    return bool((bits >> target) & 1)
