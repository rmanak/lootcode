def findKthLargest(nums, k):
    import heapq
    return heapq.nlargest(k, nums)[-1]
