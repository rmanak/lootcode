def numTriplets(nums1, nums2):
    from collections import Counter

    def count(a, b):
        res = 0
        for x in a:
            sq = x * x
            seen = Counter()
            for v in b:
                if sq % v == 0 and (sq // v) in seen:
                    res += seen[sq // v]
                seen[v] += 1
        return res

    return count(nums1, nums2) + count(nums2, nums1)
