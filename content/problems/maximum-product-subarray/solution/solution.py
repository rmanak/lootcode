def maxProduct(nums):
    best = cur_max = cur_min = nums[0]
    for x in nums[1:]:
        cands = (x, cur_max * x, cur_min * x)
        cur_max = max(cands)
        cur_min = min(cands)
        best = max(best, cur_max)
    return best
