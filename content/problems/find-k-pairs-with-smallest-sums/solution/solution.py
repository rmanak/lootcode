def kSmallestPairs(nums1, nums2, k):
    import heapq
    if not nums1 or not nums2:
        return []
    res = []
    heap = [(nums1[0] + nums2[0], 0, 0)]
    visited = {(0, 0)}
    while heap and len(res) < k:
        s, i, j = heapq.heappop(heap)
        res.append(s)
        if i + 1 < len(nums1) and (i + 1, j) not in visited:
            visited.add((i + 1, j))
            heapq.heappush(heap, (nums1[i + 1] + nums2[j], i + 1, j))
        if j + 1 < len(nums2) and (i, j + 1) not in visited:
            visited.add((i, j + 1))
            heapq.heappush(heap, (nums1[i] + nums2[j + 1], i, j + 1))
    return res
