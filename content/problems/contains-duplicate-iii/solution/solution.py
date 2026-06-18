def containsNearbyAlmostDuplicate(nums, k, t):
    if k <= 0 or t < 0:
        return False
    w = t + 1
    buckets = {}
    for i, x in enumerate(nums):
        b = x // w
        if b in buckets:
            return True
        if b - 1 in buckets and x - buckets[b - 1] <= t:
            return True
        if b + 1 in buckets and buckets[b + 1] - x <= t:
            return True
        buckets[b] = x
        if i >= k:
            del buckets[nums[i - k] // w]
    return False
