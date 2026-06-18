def countPairs(nums, target):
    from collections import defaultdict
    seen = defaultdict(int)
    count = 0
    for x in nums:
        count += seen[target - x]
        seen[x] += 1
    return count
