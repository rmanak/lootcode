def partitionDisjoint(nums):
    n = len(nums)
    left_max = nums[0]
    cur_max = nums[0]
    partition = 0
    for i in range(1, n):
        if nums[i] < left_max:
            partition = i
            left_max = cur_max
        else:
            cur_max = max(cur_max, nums[i])
    return partition + 1
