def numberOfSubarrays(nums, k):
    from collections import defaultdict
    count = defaultdict(int)
    count[0] = 1
    odd = 0
    res = 0
    for x in nums:
        odd += x % 2
        res += count[odd - k]
        count[odd] += 1
    return res
