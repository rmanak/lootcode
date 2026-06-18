def maxSubarraySumCircular(nums):
    total = sum(nums)
    cur_max = 0
    best_max = float('-inf')
    cur_min = 0
    best_min = float('inf')
    for x in nums:
        cur_max = max(cur_max + x, x)
        best_max = max(best_max, cur_max)
        cur_min = min(cur_min + x, x)
        best_min = min(best_min, cur_min)
    if best_max < 0:
        return best_max
    return max(best_max, total - best_min)
