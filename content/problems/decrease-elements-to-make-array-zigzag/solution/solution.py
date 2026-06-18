def movesToMakeZigzag(nums):
    n = len(nums)

    def cost(start):
        res = 0
        for i in range(start, n, 2):
            left = nums[i - 1] if i > 0 else float('inf')
            right = nums[i + 1] if i + 1 < n else float('inf')
            target = min(left, right) - 1
            if nums[i] > target:
                res += nums[i] - target
        return res

    return min(cost(0), cost(1))
