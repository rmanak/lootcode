def canPartitionKSubsets(nums, k):
    total = sum(nums)
    if total % k != 0:
        return False
    target = total // k
    nums.sort(reverse=True)
    if nums[0] > target:
        return False
    used = [False] * len(nums)

    def dfs(start, k_left, cur):
        if k_left == 0:
            return True
        if cur == target:
            return dfs(0, k_left - 1, 0)
        for i in range(start, len(nums)):
            if not used[i] and cur + nums[i] <= target:
                used[i] = True
                if dfs(i + 1, k_left, cur + nums[i]):
                    return True
                used[i] = False
                if cur == 0:
                    break
        return False

    return dfs(0, k, 0)
