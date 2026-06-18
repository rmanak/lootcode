def minSubarray(nums, p):
    total = sum(nums) % p
    if total == 0:
        return 0
    n = len(nums)
    pre = 0
    last = {0: -1}
    res = n
    for i, x in enumerate(nums):
        pre = (pre + x) % p
        need = (pre - total) % p
        if need in last:
            res = min(res, i - last[need])
        last[pre] = i
    return res if res < n else -1
