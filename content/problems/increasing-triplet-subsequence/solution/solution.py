def increasingTriplet(nums):
    first = second = float('inf')
    for x in nums:
        if x <= first:
            first = x
        elif x <= second:
            second = x
        else:
            return True
    return False
