def maxValueAfterReverse(nums):
    n = len(nums)
    total = sum(abs(nums[i] - nums[i + 1]) for i in range(n - 1))
    best = 0
    for j in range(n - 1):
        best = max(best, abs(nums[0] - nums[j + 1]) - abs(nums[j] - nums[j + 1]))
        best = max(best, abs(nums[n - 1] - nums[j]) - abs(nums[j] - nums[j + 1]))
    hi, lo = float('-inf'), float('inf')
    for i in range(n - 1):
        a, b = nums[i], nums[i + 1]
        hi = max(hi, min(a, b))
        lo = min(lo, max(a, b))
    best = max(best, 2 * (hi - lo))
    return total + best
