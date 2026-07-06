def removeDuplicates(nums):
    res = []
    for x in nums:
        if len(res) < 2 or res[-2] != x:
            res.append(x)
    return res
