def kLengthApart(nums, k):
    prev = -1
    for i, x in enumerate(nums):
        if x == 1:
            if prev != -1 and i - prev - 1 < k:
                return False
            prev = i
    return True
