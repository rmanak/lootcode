def subarraysWithKDistinct(A, K):
    from collections import defaultdict

    def atMost(k):
        count = defaultdict(int)
        res = 0
        l = 0
        for r in range(len(A)):
            count[A[r]] += 1
            while len(count) > k:
                count[A[l]] -= 1
                if count[A[l]] == 0:
                    del count[A[l]]
                l += 1
            res += r - l + 1
        return res

    return atMost(K) - atMost(K - 1)
