def singleNumber(nums):
    return (3 * sum(set(nums)) - sum(nums)) // 2
