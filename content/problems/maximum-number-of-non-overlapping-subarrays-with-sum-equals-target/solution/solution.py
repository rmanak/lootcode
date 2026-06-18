def maxNonOverlapping(nums, target):
    seen = {0}
    prefix = 0
    count = 0
    for x in nums:
        prefix += x
        if prefix - target in seen:
            count += 1
            seen = {0}
            prefix = 0
        else:
            seen.add(prefix)
    return count
