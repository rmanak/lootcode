def checkSubarraySum(nums, k):
    seen = {0: -1}
    pre = 0
    for i, x in enumerate(nums):
        pre += x
        r = pre % k if k != 0 else pre
        if r in seen:
            if i - seen[r] >= 2:
                return True
        else:
            seen[r] = i
    return False
