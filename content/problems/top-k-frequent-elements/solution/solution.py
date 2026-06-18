def topKFrequent(nums, k):
    from collections import Counter
    c = Counter(nums)
    order = sorted(c.keys(), key=lambda v: (-c[v], v))
    return sorted(order[:k])
