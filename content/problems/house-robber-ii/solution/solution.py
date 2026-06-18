def rob(nums):
    def rob_line(arr):
        prev = cur = 0
        for x in arr:
            prev, cur = cur, max(cur, prev + x)
        return cur

    if len(nums) == 1:
        return nums[0]
    return max(rob_line(nums[1:]), rob_line(nums[:-1]))
