def summaryRanges(nums):
    res = []
    i, n = 0, len(nums)
    while i < n:
        j = i
        while j + 1 < n and nums[j + 1] == nums[j] + 1:
            j += 1
        if i == j:
            res.append(str(nums[i]))
        else:
            res.append(f"{nums[i]}->{nums[j]}")
        i = j + 1
    return res
