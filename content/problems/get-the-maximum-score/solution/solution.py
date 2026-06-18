def maxSum(nums1, nums2):
    MOD = 10 ** 9 + 7
    i = j = 0
    s1 = s2 = 0
    n, m = len(nums1), len(nums2)
    res = 0
    while i < n or j < m:
        if i < n and (j == m or nums1[i] < nums2[j]):
            s1 += nums1[i]
            i += 1
        elif j < m and (i == n or nums2[j] < nums1[i]):
            s2 += nums2[j]
            j += 1
        else:
            res += max(s1, s2) + nums1[i]
            s1 = s2 = 0
            i += 1
            j += 1
    res += max(s1, s2)
    return res % MOD
