def maxJumps(arr, d):
    import sys
    sys.setrecursionlimit(5000)
    n = len(arr)
    from functools import lru_cache

    @lru_cache(None)
    def dp(i):
        best = 1
        for step in (-1, 1):
            for x in range(1, d + 1):
                j = i + step * x
                if not (0 <= j < n) or arr[j] >= arr[i]:
                    break
                best = max(best, 1 + dp(j))
        return best

    return max(dp(i) for i in range(n))
