def longestSubarray(nums, limit):
    from collections import deque
    maxd = deque()
    mind = deque()
    l = 0
    best = 0
    for r, x in enumerate(nums):
        while maxd and nums[maxd[-1]] <= x:
            maxd.pop()
        maxd.append(r)
        while mind and nums[mind[-1]] >= x:
            mind.pop()
        mind.append(r)
        while nums[maxd[0]] - nums[mind[0]] > limit:
            l += 1
            if maxd[0] < l:
                maxd.popleft()
            if mind[0] < l:
                mind.popleft()
        best = max(best, r - l + 1)
    return best
