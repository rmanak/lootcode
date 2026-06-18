def containsNearbyAlmostDuplicate(nums, indexDiff, valueDiff):
    if indexDiff <= 0 or valueDiff < 0:
        return False
    width = valueDiff + 1
    buckets = {}
    for i, x in enumerate(nums):
        b = x // width
        if b in buckets:
            return True
        if b - 1 in buckets and abs(x - buckets[b - 1]) <= valueDiff:
            return True
        if b + 1 in buckets and abs(x - buckets[b + 1]) <= valueDiff:
            return True
        buckets[b] = x
        if i >= indexDiff:
            del buckets[nums[i - indexDiff] // width]
    return False
