def getMaxLen(nums):
    pos = neg = 0
    best = 0
    for x in nums:
        if x == 0:
            pos = neg = 0
        elif x > 0:
            pos += 1
            neg = neg + 1 if neg > 0 else 0
        else:
            new_pos = neg + 1 if neg > 0 else 0
            new_neg = pos + 1
            pos, neg = new_pos, new_neg
        best = max(best, pos)
    return best
