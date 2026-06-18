def findMaximumXOR(nums):
    mask = 0
    res = 0
    for i in range(31, -1, -1):
        mask |= (1 << i)
        prefixes = {x & mask for x in nums}
        cand = res | (1 << i)
        if any((cand ^ p) in prefixes for p in prefixes):
            res = cand
    return res
