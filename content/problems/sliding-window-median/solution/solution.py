def medianSlidingWindow(nums, k):
    import bisect
    window = sorted(nums[:k])
    res = [window[k // 2]]
    for i in range(k, len(nums)):
        window.pop(bisect.bisect_left(window, nums[i - k]))
        bisect.insort(window, nums[i])
        res.append(window[k // 2])
    return res
