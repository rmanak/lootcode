def xorGame(nums):
    x = 0
    for v in nums:
        x ^= v
    return x == 0 or len(nums) % 2 == 0
