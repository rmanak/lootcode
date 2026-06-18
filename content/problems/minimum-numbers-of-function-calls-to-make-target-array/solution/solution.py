def minOperations(nums):
    increments = 0
    max_doublings = 0
    for x in nums:
        increments += bin(x).count("1")
        if x > 0:
            max_doublings = max(max_doublings, x.bit_length() - 1)
    return increments + max_doublings
