def removeDuplicates(nums):
    out = []
    for x in nums:
        if not out or out[-1] != x:
            out.append(x)
    return out
