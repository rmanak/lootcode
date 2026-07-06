def merge(nums1, m, nums2, n):
    a = nums1[:m]
    b = nums2[:n]
    res, i, j = [], 0, 0
    while i < m and j < n:
        if a[i] <= b[j]:
            res.append(a[i]); i += 1
        else:
            res.append(b[j]); j += 1
    res.extend(a[i:]); res.extend(b[j:])
    return res
